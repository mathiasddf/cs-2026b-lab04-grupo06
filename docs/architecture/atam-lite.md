## Evaluación ATAM-lite Cruzada — Emitida por Grupo 06 (RutaSIT Arequipa)

Hemos revisado su `arbol.dot` (E1) y su `add/iteracion-1.md` (E2) contrastando los hallazgos del evaluador adversario con su evidencia cuantitativa:

1. **Punto de sensibilidad:** El `p95` de su flujo principal en hora pico depende fuertemente de la tasa de aciertos (*hit ratio*) de la caché y de la latencia de la consulta subyacente en base de datos cuando la caché está fría (0%–20% de aciertos).
2. **Punto de trade-off:** Introducir caché con TTL mejora drásticamente el rendimiento (`p95`), pero degrada la frescura de los datos mostrados al usuario durante la ventana del TTL (consistencia temporal vs. latencia).
3. **Riesgo R1 (Probabilidad: 4/5, Impacto: 5/5 — Zona Crítica):** Dependencia síncrona del servicio externo en el flujo principal con solo reintentos simples. Si el proveedor externo sufre una caída sostenida de 15–20 minutos, los reintentos por solicitud agotarán los *workers* del VPS provocando denegación de servicio en cascada.
   - *Pregunta incómoda:* ¿Qué ocurre con los 4 workers de su VPS si el proveedor externo da timeout de 3 s durante 15 minutos seguidos y llegan 15 req/s?
4. **Riesgo R2 (Probabilidad: 3/5, Impacto: 4/5 — Zona Crítica):** Despliegue en un único VPS constituye un punto único de falla (SPOF) de infraestructura para la disponibilidad del servicio.
   - *Pregunta incómoda:* Si el VPS se reinicia o pierde la caché en memoria en plena hora pico, ¿en cuántos minutos se recupera el servicio sin perder operaciones?
5. **No riesgo:** Mantener el estilo arquitectónico de **Monolito Modular (`ADR-001`)** es una decisión segura y respaldada por su simulación M/G/c, ya que con optimización de consultas e índices el `p95` se mantiene muy por debajo del presupuesto sin necesidad de microservicios.