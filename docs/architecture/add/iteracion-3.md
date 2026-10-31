# Iteración 3 de ADD 3.0 — Seguridad Multiconcesionaria y Modificabilidad de Rutas (QA-04 y QA-06)

## 1. Paso 1 y 2: Objetivos de la iteración
- **Escenario QA-04 (H,M) — Seguridad e integridad:** Con 1200 buses pertenecientes a 8 empresas concesionarias distintas del SIT Arequipa, si el sistema de una concesionaria A intenta inyectar telemetría falsa o consultar datos internos de operación de las unidades de la concesionaria B, el 100% de los intentos es rechazado con HTTP 403 (`AccesoCruzadoConcesionariaError`) y se exponen 0 filas cruzadas.
- **Escenario QA-06 (H,M) — Modificabilidad:** Cuando la Municipalidad Provincial de Arequipa modifica el trazado de un corredor o declara un desvío temporal por obras viales, el cambio se aplica en $\le 2\text{ horas}$ sin recompilar ni desplegar código Python.

## 2. Paso 3 y 4: Evaluación de alternativas de diseño (con apoyo crítico de IA)

### Tabla comparativa 3A — Aislamiento y seguridad entre concesionarias (QA-04)

| Alternativa propuesta por la IA | Aislamiento (QA-04) | Costo operativo al incorporar otra concesionaria | Impacto en consultas de pasajeros | Decisión del equipo |
| :--- | :--- | :--- | :--- | :--- |
| **1. Una base de datos PostgreSQL por concesionaria (8 BDs)** | Muy alto (físico) | Alto: requiere migrar 8 bases y hacer federated queries cuando un pasajero consulta una avenida donde circulan 4 empresas | Empeora la latencia de QA-01 al unir resultados de múltiples BDs | **Rechazada:** Operación compleja en un solo VPS y rompe las consultas unificadas por paradero. |
| **2. Un esquema PostgreSQL por concesionaria** | Alto | Medio: obliga a ejecutar migraciones Alembic/SQL repetidas por cada esquema | Requiere UNION ALL entre esquemas para calcular ETAs en corredores compartidos | **Rechazada:** Ineficiente para consultas geoespaciales transversales del SIT. |
| **3. Tabla unificada con columna concesionaria_id + Row-Level Security (RLS) en PostgreSQL + Claim firmado en JWT (ADR-008)** | Alto (garantizado por motor PostgreSQL y validado en el servicio) | Muy rápido: insertar 1 fila en la tabla concesionarias y emitir su par de llaves JWT | Óptimo: el módulo de pasajeros lee sobre el índice unificado y cada operador solo ve/escribe sus filas | **Aceptada (ADR-008):** Mitigada con la fitness function `test_ff06_aislamiento_multiconcesionaria_cero_fugas`. |

### Tabla comparativa 3B — Modificabilidad de rutas y desvíos (QA-06 — Táctica "Diferir el enlace / Configuración en BD")

| Alternativa evaluada | Tiempo para aplicar un desvío municipal | ¿Requiere despliegue de código? | Riesgo / Trade-off | Decisión del equipo |
| :--- | :--- | :---: | :--- | :--- |
| **Geometrías y segmentos fijos en código Python** (`SegmentoRuta` hardcodeado) | 1 a 2 días (PR, CI y redespliegue) | Sí | Cualquier obra vial urgente en Arequipa deja desactualizados los avisos de DESVIADO | **Rechazada** |
| **Parametrización dinámica en tablas PostGIS** compatibles con GTFS (`corredores_geom`, `paraderos`, `desvios_activos`) con recarga en caliente | $\le 15\text{ minutos}$ desde el panel del operador SIT | No (0 despliegues) | **Trade-off:** un polígono mal cargado en BD puede marcar falsos desvíos; se mitiga con validación geométrica al guardar (ADR-008) | **Aceptada (ADR-008)** |

## 3. Paso 5, 6 y 7: Verificación automatizada
Se implementó la verificación de `claim_jwt_operador` y el filtrado tipo RLS en `ServicioConsultas.registrar_telemetria_operador()` y `consultar_telemetria_concesionaria()` (`src/consultas/servicio.py`), comprobados automáticamente mediante la fitness function `test_ff06_aislamiento_multiconcesionaria_cero_fugas` en `tests/test_fitness.py`.