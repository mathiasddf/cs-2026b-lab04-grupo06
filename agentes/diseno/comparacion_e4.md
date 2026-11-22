# Comparación E2 vs. E4: impacto de `mapa_repo` y memoria de notas (`anotar` / `leer_notas`)

Este documento compara de forma objetiva la ejecución del agente ReAct sin herramientas de mapa ni memoria persistente en **E2 (`ISSUE-01`)** frente a la ejecución con la herramienta nueva **`mapa_repo`** (análisis estático AST) y la **memoria de notas** en `notas.md` (`anotar` / `leer_notas`) en **E4 (`ISSUE-03`)**.

## Tabla comparativa real (medida desde trazas y ejecuciones reproducibles)

| Métrica | E2 — `ISSUE-01` (ReAct base) | E4 — `ISSUE-03` (ReAct + `mapa_repo` + notas) | Diferencia (E4 vs. E2) |
| :--- | :---: | :---: | :---: |
| Archivo de traza | `agentes/trazas/issue01_react.jsonl` | `agentes/trazas/issue03_memoria.jsonl` | — |
| Diagrama de trayectoria | `agentes/trazas/issue01_react.png` | `agentes/trazas/issue03_memoria.png` | — |
| Evidencia de memoria externa | *(no aplica)* | `agentes/trazas/notas_issue03.md` | Memoria persistente en `notas.md` |
| Pasos totales (acciones + `final`) | **9** | **10** | +1 paso |
| Llamadas a herramientas totales | **8** (7 válidas + 1 rechazada) | **9** (9 válidas) | +1 llamada (+2 válidas) |
| Desglose de herramientas | `leer_archivo` (2), `ejecutar_comando` (3), `buscar` (1), `editar_archivo` (1), `(ninguna)` (1) | `leer_archivo` (2), `mapa_repo` (1), `ejecutar_comando` (3), `anotar` (1), `editar_archivo` (1), `leer_notas` (1) | Reemplaza `buscar` por `mapa_repo`; añade `anotar` y `leer_notas` |
| Errores de contrato (`CONTRATO_INVALIDO`) | **1** (`aplicar_parche`) | **0** | -1 error de contrato |
| Bloqueos de política (`BLOQUEADO`) | **0** | **0** | Igual |
| Contexto final (`historial`) | **10 988 caracteres** (~2 747 tokens) | **26 221 caracteres** (~6 555 tokens) | +15 233 caracteres (+138,6 %) |
| Resultado de pruebas del issue | `tests/test_issue_01.py`: **2/2 PASSED** | `tests/test_issue_03.py`: **5/5 PASSED** | Ambos en verde |
| Complejidad ciclomática (`radon cc`) | Grado **A** (`calcular_eta_a_paradero`: 3) | Grado **A** (`normalizar_trama_gps`: 4, helpers: 4) | Grado A en ambos |

## Análisis objetivo: ¿necesitó menos pasos o menos contexto?

1. **Pasos totales (10 en E4 vs. 9 en E2):**
   - E4 **no** redujo el número absoluto de pasos, pero eliminó por completo los errores de contrato (**0** frente a **1** en E2) y reemplazó `buscar` por `mapa_repo("src/consultas")`.
   - El incremento neto de +1 paso proviene exclusivamente del uso disciplinado de la memoria de notas (`anotar` antes de editar y `leer_notas` antes de emitir el resumen final), lo que aporta trazabilidad de hipótesis y archivos revisados.

2. **Consumo de contexto final (26 221 caracteres en E4 vs. 10 988 en E2):**
   - En un issue puntual de un solo archivo donde el reporte (`ISSUE-03.md`) ya menciona el módulo afectado, E4 consumió **más contexto** que E2 por tres causas medibles:
     - `mapa_repo("src/consultas")` recorrió todos los archivos `.py` bajo `src/consultas` (167 líneas, 8 284 caracteres, incluyendo `src/consultas/antes/servicio.py`), frente a `buscar("def calcular_eta_a_paradero")` en E2 que devolvió una sola línea (64 caracteres).
     - `src/consultas/proveedores_gps.py` (105 líneas) es casi el doble de extenso que `src/consultas/estrategias_eta.py` (57 líneas), y la reproducción inicial de `ISSUE-03` falló en 4 casos parametrizados (2 000 caracteres de traza de `pytest`) frente a 1 solo fallo en `ISSUE-01`.
     - Las descripciones detalladas de las 3 nuevas herramientas en `catalogo()` y las 2 interacciones de `notas.md` agregaron ~1 750 caracteres al historial.

3. **Cuándo compensan `mapa_repo` y la memoria de notas:**
   - Aunque `mapa_repo("src/consultas")` ocupó 8 284 caracteres, leer completos los 11 archivos de `src/consultas` habría consumido más de 30 000 caracteres (~73 % de ahorro frente a lectura completa). Su valor real aparece en **issues multifichero** o cuando el reporte no indica qué archivo tocar.
   - Si se invoca `mapa_repo` sobre una subruta acotada (o excluyendo carpetas heredadas como `antes/`), el costo en contexto cae drásticamente.
   - La **memoria de notas (`notas.md`)** introduce un pequeño costo fijo en tareas cortas (<12 pasos), pero resulta decisiva en tareas largas o multiagente (donde la ventana de contexto se compacta o se transfiere trabajo entre rondas) porque preserva decisiones, hipótesis y archivos revisados fuera del historial efímero.
