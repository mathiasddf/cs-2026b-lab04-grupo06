# Lienzo de Diseño del Sistema Agéntico — RutaSIT Arequipa (Lab 10)

> **Proyecto:** RutaSIT Arequipa (Caso 6 — `cs-2026b-lab04-grupo06`)  
> **Entregable:** E1 — Lienzo de diseño y tareas del agente  
> **Alcance:** Sistema agéntico para diagnosticar, corregir y verificar issues en el módulo de consultas (`src/consultas/`) respetando los contratos arquitectónicos (`FF-01`, `FF-02`) y las pruebas automatizadas del repositorio.

---

## 1. Las 7 decisiones de diseño justificadas

| # | Decisión de diseño | Elección para RutaSIT Arequipa | Justificación técnica y respaldo bibliográfico |
|---|---|---|---|
| **1** | **¿Agente o flujo de trabajo?** | **Agente** para la resolución de issues en `src/consultas/`.<br>**Flujo de trabajo fijo** para pipelines lineales del repositorio (p. ej., el pipeline del Lab 09). | Resolver un issue real en `src/consultas/` requiere explorar archivos cuya ubicación no se conoce de antemano, formular hipótesis sobre la causa raíz, editar código, ejecutar `pytest` y reaccionar a fallos inesperados o regresiones en ciclos variables. En cambio, tareas de RutaSIT con pasos deterministas y siempre idénticos —como el **pipeline del Lab 09: Historia de usuario → validación de criterios INVEST → generación de pruebas `pytest`** (`src/consultas/generador_criterios.py` y `prompts/`)— se resuelven mejor con un **flujo de trabajo fijo**, evitando costo, latencia y variabilidad innecesarios. |
| **2** | **Arquetipo** | **Planificador-ejecutor + ReAct** | Basado en la **Sección 1.3** (*Albada, 2025, cap. 5; Yao et al., 2023*): el componente **planificador-ejecutor** produce primero un plan breve, trazable y auditable antes de tocar código, mientras que la ejecución de cada paso utiliza el bucle **ReAct** (*pensamiento → acción → observación*) para inspeccionar módulos reales (`estrategias_eta.py`, `estados.py`, `proveedores_gps.py`), reproducir el fallo en rojo y ajustar la corrección iterativamente según la salida real de las pruebas. |
| **3** | **Herramientas** | Conjunto mínimo inicial: `listar_archivos`, `leer_archivo`, `buscar`, `editar_archivo`, `ejecutar_pruebas`, `ver_cambios`, `ejecutar_comando` (con lista permitida: `pytest`, `radon`, `lint-imports`, `git status`, `git diff`).<br>Extensión en **E4**: `mapa_repo`, `anotar`, `leer_notas`. | Cada herramienta encapsula una operación verificable y acotada sobre el repositorio de RutaSIT. La lista permitida en `ejecutar_comando` habilita la verificación de calidad (pruebas unitarias, complejidad ciclomática con `radon` y contratos de capas `FF-01`/`FF-02` con `lint-imports`) impidiendo la ejecución arbitraria de comandos externos (como `curl`, `sh` o descargas no autorizadas). En E4, `mapa_repo` acelera la navegación del código y `anotar`/`leer_notas` externalizan hallazgos entre pasos. |
| **4** | **Memoria** | **Corto plazo** (historial de la tarea en la ventana de contexto) + **memoria de notas/pizarra** (`notas.md` en E4). | La memoria a corto plazo mantiene la secuencia inmediata de observaciones, diffs y salidas de `pytest` dentro de la sesión activa. Al incorporar en E4 una pizarra persistente de trabajo (`notas.md` mediante `anotar`/`leer_notas`), el agente conserva hipótesis descartadas, archivos inspeccionados y contratos detectados sin saturar la ventana de contexto ni repetir lecturas redundantes. |
| **5** | **Coordinación** | **Por gestor (planificador) + actor-crítico (ejecutor y revisor de solo lectura)** | Fundamentado en la **Sección 1.7** (*Albada, 2025, cap. 8; Koenigstein, 2026, cap. 2*): aplica **descomposición** (planificar, implementar y auditar son fases separadas), **especialización** (cada rol tiene un prompt e intención precisos), **mínimo privilegio** (el revisor crítico solo tiene herramientas de lectura, `ver_cambios` y `ejecutar_pruebas`, nunca `editar_archivo`) y **principio de parsimonia** (solo los roles estrictamente necesarios, sin multiplicar agentes redundantes). Esta separación también protege frente a inyecciones indirectas en comentarios del código. |
| **6** | **Rol humano** | **Revisor (*human-in-the-loop*)** con proyección a delegación progresiva. | El ingeniero humano mantiene la autoridad final: aprueba ediciones sensibles mediante el gancho `aprobar_edicion` y revisa/fusiona cada Pull Request en GitHub tras verificar el diff, las pruebas y las trazas. Conforme el sistema acumule evidencia empírica en la evaluación de E5, el nivel de autonomía puede escalar de forma progresiva en cambios de bajo riesgo. |
| **7** | **Control** | Defensa en profundidad: contrato JSON estructurado, mínimo privilegio por rol, sandbox de rutas, rutas protegidas (`tests/`), lista permitida de comandos, límites de pasos y rondas, y trazas JSONL. | Antes de invocar cualquier herramienta se valida el **contrato estructurado JSON** de la acción; cada rol opera bajo **mínimo privilegio**; todas las rutas se restringen al **sandbox** del directorio de trabajo; `tests/` es **ruta protegida** (el ejecutor no puede modificar las pruebas para "hacerlas pasar"); `ejecutar_comando` solo acepta la lista permitida; se fijan techos estrictos (`max_pasos=12` para el ejecutor, `max_pasos=8` para el revisor y máximo **2 rondas actor-crítico**); y cada paso se registra en **trazas JSONL** auditables. |

---

## 2. Issues objetivo de RutaSIT Arequipa y criterio objetivo de resolución (enfoque SWE-bench)

Para evaluar al sistema agéntico de forma reproducible y sin sesgos subjetivos, adoptamos el enfoque **SWE-bench**: cada tarea se define mediante un **issue en lenguaje natural** (`issues/ISSUE-0N.md`) acompañado de una **prueba automatizada en rojo** (`tests/test_issue_0N.py`) que el agente **no puede editar** (`tests/` está protegida). Un issue se considera objetivamente **resuelto** si y solo si:

1. La prueba en rojo del issue pasa a **verde** (`PASSED`).
2. Las **24 pruebas previas** de la suite (`test_comportamiento.py`, `test_patrones.py`, `test_fitness.py`, `test_generador_prompts.py`) siguen pasando **24/24** sin regresiones.
3. Los contratos arquitectónicos de `.importlinter` (**FF-01** y **FF-02**) permanecen en estado **KEPT**.

### Resumen de los 3 issues objetivo

| Issue | Módulo afectado | Descripción del defecto | Prueba que define "resuelto" |
|---|---|---|---|
| **[ISSUE-01](../../issues/ISSUE-01.md)** | `src/consultas/estrategias_eta.py` | `calcular_eta_a_paradero` retorna un ETA negativo cuando el bus ya superó la posición kilométrica del paradero (`posicion_bus_km > posicion_paradero_km`). | `tests/test_issue_01.py::test_issue_01_eta_no_negativo_si_bus_paso_paradero` |
| **[ISSUE-02](../../issues/ISSUE-02.md)** | `src/consultas/estados.py` | `esta_en_corredor_curva` usa solo el rectángulo envolvente (*bounding box*) de la polilínea, por lo que no detecta desvíos en tramos curvos (p. ej., curva Av. Ejército → Cayma). Además contiene un comentario simulado de inyección indirecta para validar controles en E5. | `tests/test_issue_02.py::test_issue_02_detecta_desvio_en_curva` |
| **[ISSUE-03](../../issues/ISSUE-03.md)** | `src/consultas/proveedores_gps.py` | `normalizar_trama_gps` accede directamente a `trama["lat"]`, `trama["lon"]` y `trama["velocidad"]` sin validar `None` ni claves faltantes, colapsando con `KeyError`/`TypeError` en lugar de lanzar `DatosGPSIncompletosError`. | `tests/test_issue_03.py::test_issue_03_maneja_gps_sin_datos` |
