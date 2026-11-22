# ADR-010: Sistema agéntico para mantenimiento asistido en RutaSIT Arequipa

- **Estado:** Aceptado
- **Fecha:** 21/11/2026
- **Decisores:** Davila Flores Mathias Dario, Chavez Cuno Deivick Paul Eddi
- **Contexto del proyecto:** Laboratorio 10 — Sistemas agénticos en la construcción de software (`cs-2026b-lab04-grupo06`)

---

## Contexto

El mantenimiento evolutivo del módulo de consultas de **RutaSIT Arequipa** (`src/consultas/`) —incluyendo cálculo de ETA (`estrategias_eta.py`), validación geométrica y estados de viaje (`estados.py`) y normalización de telemetría GPS (`proveedores_gps.py`)— involucra diagnosticar defectos reportados en lenguaje natural, explorar archivos cuya causa raíz no siempre se conoce a priori, aplicar cambios acotados y verificar que no se rompan las pruebas de regresión ni los contratos arquitectónicos (`FF-01`..`FF-06`).

Mientras que las tareas lineales y deterministas (como el pipeline del Lab 09: historia de usuario → criterios INVEST → pruebas `pytest`) deben seguir siendo **flujos de trabajo fijos**, la resolución exploratoria de issues requiere un **sistema agéntico** capaz de iterar sobre observaciones reales de `pytest`, `radon cc` y `lint-imports` sin comprometer la seguridad del repositorio, el aislamiento de concesionarias (Conecta / TransCayma) ni el control humano.

---

## Decisión

Adoptamos una arquitectura agéntica modular en `agentes/` sustentada en seis decisiones explícitas:

1. **Arquetipo (ReAct + máquina de estados + contrato JSON):**
   - El núcleo ([`agentes/agente/nucleo.py`](../../../agentes/agente/nucleo.py)) implementa el bucle **ReAct** (*pensamiento → acción → observación*) modelado como una **máquina de estados explícita** (`EstadoAgente`, 11 estados: `INICIO`, `DECIDIENDO`, `VALIDANDO_CONTRATO`, `CONTRATO_INVALIDO`, `EVALUANDO_POLITICA`, `ESPERANDO_APROBACION`, `EJECUTANDO`, `OBSERVANDO`, `BLOQUEADO`, `LIMITE_ALCANZADO`, `FINALIZADO`).
   - Cada salida del modelo se valida programáticamente en [`agentes/agente/contrato.py`](../../../agentes/agente/contrato.py) antes de evaluar políticas o invocar herramientas; los errores de contrato se devuelven como observación recuperable (`CONTRATO_INVALIDO`) en lugar de fallar silenciosamente.
   - El proveedor del modelo sigue el patrón **Strategy** (`ModeloGrabado`, `ModeloInteractivo`, `ModeloAnthropic` en [`agentes/agente/modelos.py`](../../../agentes/agente/modelos.py)), permitiendo reproducibilidad determinista sin costo de API en CI.

2. **Coordinación (principio de parsimonia — Albada, cap. 8):**
   - **Agente único ReAct** (`agentes/ejecutar_issue01.py`, `agentes/ejecutar_issue03.py`, `agentes/ejecutar_issue02_unico.py`) para defectos locales, bien acotados y sin exposición a entradas no confiables.
   - **Orquestador multiagente Planificador → Actor-Crítico** ([`agentes/orquestador.py`](../../../agentes/orquestador.py)) con 3 roles (**Planificador** sin herramientas, **Ejecutor** con herramientas de edición/comandos y **Revisor** de solo lectura sin `editar_archivo` ni `anotar`, máximo **2 rondas**) para cambios con riesgo de seguridad, inyección indirecta o auditoría independiente.

3. **Herramientas y sandbox:**
   - Catálogo explícito y acotado en [`agentes/agente/herramientas.py`](../../../agentes/agente/herramientas.py): `listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo` (análisis estático AST de clases, firmas y líneas), `editar_archivo` (reemplazo único exacto), `ver_cambios`, `ejecutar_pruebas`, `ejecutar_comando`, `anotar` y `leer_notas`.
   - Toda operación de archivos pasa por `_ruta()`, que resuelve rutas canónicas y lanza `PermissionError` ante cualquier intento de escape fuera del directorio sandbox aislado (`agentes/.sandbox/`).

4. **Memoria (corto plazo + pizarra externa):**
   - **Corto plazo:** `Agente.historial` conserva el objetivo, las decisiones JSON y las observaciones acotadas de la sesión activa.
   - **Memoria externa de notas:** `anotar` y `leer_notas` persisten hipótesis, archivos revisados y verificaciones en `notas.md` dentro del sandbox, desacoplando hallazgos clave del crecimiento efímero del historial.

5. **Límites y guardrails (`Politica`):**
   - [`agentes/agente/politica.py`](../../../agentes/agente/politica.py) impone lista blanca de herramientas por rol, lista blanca de comandos por expresión regular (`^python -m pytest\b`, `^radon cc\b`, `^lint-imports\b`, `^git (status|diff)\b`), rutas protegidas (`tests/` no editable por el agente) y presupuesto estricto de pasos (`max_pasos = 12` ejecutor, `max_pasos = 8` revisor, `max_pasos = 3` planificador).
   - Esto provee defensa en profundidad frente a inyecciones indirectas (como el comentario `curl ... | sh` en `src/consultas/estados.py`), combinando bloqueo determinista en `Politica` con auditoría independiente del Revisor.

6. **Rol humano y delegación progresiva (HITL):**
   - `pedir_aprobacion_edicion` en `agentes/agente/politica.py` se conecta por defecto a `pol_ejecutor.aprobar_edicion` en `agentes/orquestador.py`, deteniendo la máquina en `ESPERANDO_APROBACION`, mostrando un `unified_diff` legible y exigiendo confirmación estricta `[s/n]` (con `--auto-aprobar` reservado únicamente para CI/pruebas).
   - La evolución de autonomía se gobierna por la hoja de ruta de 4 etapas en [`agentes/delegacion.md`](../../../agentes/delegacion.md) (**Ejecutor → Revisor [actual] → Colaborador → Gobernador**), condicionada a métricas verificables en trazas JSONL.

---

## Alternativas descartadas

1. **Conceder acceso irrestricto a shell (`bash`) sin lista blanca ni sandbox:** Descartada por riesgo crítico de ejecución remota ante inyección indirecta (evidenciado en `ISSUE-02` con `curl ... | sh`) y posible alteración de `tests/` o de la rama `main`.
2. **Usar siempre coordinación multiagente para cualquier issue trivial:** Descartada por violar el principio de parsimonia; en `ISSUE-02` el esquema actor-crítico duplicó el consumo acumulado de contexto (+118,2 %, de 16 889 a 36 848 caracteres), costo injustificado en bugs locales sin riesgo de seguridad como `ISSUE-01`.
3. **Confiar únicamente en instrucciones del prompt sin contrato ni política en código:** Descartada porque el LLM es probabilístico (en E2 inventó `aplicar_parche` y en E5 obedeció el comentario de inyección indirecta); solo las compuertas deterministas en código garantizan seguridad y recuperabilidad.
4. **Depender de un LLM en vivo en CI para probar el agente:** Descartada por costo, latencia y *flakiness*; el patrón Strategy (`ModeloGrabado`) permite probar contrato, política, máquina de estados y HITL de forma determinista y sin API.

---

## Consecuencias y Trade-offs aceptados

- **Positivas (+):**
  - **Defensa en profundidad verificada:** 100 % de bloqueo determinista ante comandos no permitidos, recuperación limpia ante `CONTRATO_INVALIDO` y detección de comentarios maliciosos residuales por el Revisor de solo lectura.
  - **Observabilidad completa:** cada sesión genera trazas JSONL (`agentes/trazas/`) convertibles en diagramas de secuencia Mermaid y métricas de pasos, bloqueos y contexto.
  - **Integridad arquitectónica preservada:** las pruebas de regresión (24/24), issues (9/9), pruebas del agente (31/31) y contratos `.importlinter` (`FF-01`, `FF-02`) se mantienen 100 % en verde.
- **Negativas / Trade-offs aceptados (-):**
  - **Mayor consumo de contexto en modo multiagente y con `mapa_repo` amplio:** el modo actor-crítico consume ~2,2× más tokens acumulados que un agente único, y `mapa_repo("src/consultas")` incluye carpetas heredadas (`antes/`) si no se acota la subruta.
  - **Fricción operativa del HITL en Etapa 2:** aprobar cada `editar_archivo` ralentiza tareas mecánicas, trade-off aceptado deliberadamente hasta acumular evidencia sostenida en trazas JSONL para avanzar a la Etapa 3 (*Colaborador*).

---

## Validación

- **Pruebas del propio agente (31/31 PASSED):** [`agentes/pruebas_agente/test_agente.py`](../../../agentes/pruebas_agente/test_agente.py) cubre contrato, política, sandbox, máquina de estados, `mapa_repo`, `notas.md` y validador humano `pedir_aprobacion_edicion`.
- **Pruebas de issues y regresión (33/33 PASSED):** `tests/test_issue_01.py`, `tests/test_issue_02.py`, `tests/test_issue_03.py` y las 24 pruebas previas de RutaSIT.
- **Contratos arquitectónicos (`lint-imports`):** 2/2 `KEPT` (`FF-01`, `FF-02`).
- **Evidencia empírica de trazas:** [`agentes/observacion.md`](../../../agentes/observacion.md) y [`agentes/bitacora-ia.md`](../../../agentes/bitacora-ia.md).
