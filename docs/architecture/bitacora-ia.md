# Bitácora de uso de IA — RutaSIT Arequipa

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 04/10/2026 | ChatGPT | Proponer 3 alternativas arquitectónicas para RutaSIT considerando drivers, equipo, plazo y presupuesto. | Monolito modular, arquitectura orientada a eventos y microservicios. Recomendó inicialmente monolito modular. | Verificamos la recomendación frente a QA-01, R-01 y R-02. La recomendación se mantuvo como candidata, pero no como decisión automática. | Aceptada |
| 2 | 04/10/2026 | ChatGPT | Realizar una crítica adversarial a la recomendación de monolito modular para RutaSIT. | Identificó riesgos de escalabilidad, procesamiento síncrono, aislamiento de fallos y crecimiento futuro; destacó ventajas de una arquitectura orientada a eventos. | Verificamos que 300 buses enviando cada 10 s equivalen en promedio a 30 actualizaciones/s y que ese dato por sí solo no demuestra la necesidad de una arquitectura distribuida. | Corregida |

## Anexo: prompts

### Prompt 1 — Alternativas arquitectónicas

Actúa como arquitecto de software y propón 3 alternativas de estilo arquitectónico para el MVP de RutaSIT Arequipa, un sistema de seguimiento en tiempo real de buses.

El sistema debe permitir consultar la ubicación de buses en un mapa, calcular el tiempo estimado de llegada (ETA) a los paraderos, gestionar alertas de desvío o congestión y permitir la supervisión del servicio. Como requisito crítico de rendimiento, 300 buses con GPS envían su posición cada 10 segundos y el ETA debe actualizarse en un máximo de 15 segundos.

Los atributos de calidad priorizados son rendimiento, fiabilidad, disponibilidad, escalabilidad y modificabilidad. El MVP debe estar en producción en 1 mes, el equipo está formado por 2 integrantes con conocimientos en Python, Java, MySQL y Git/GitHub, y el presupuesto es bajo, por lo que deben priorizarse soluciones de código abierto o de bajo costo. Además, el sistema depende de los datos de ubicación proporcionados por los dispositivos GPS de los buses.

Propón exactamente 3 alternativas de estilo arquitectónico viables. Para cada una, explica en 2 o 3 líneas cómo se organizaría el sistema y señala brevemente sus principales ventajas y desventajas para estos drivers. Finalmente, recomienda una de las tres alternativas para este MVP y justifica la recomendación. La recomendación será evaluada posteriormente por el equipo y no se asumirá como decisión definitiva.

### Prompt 2 — Crítica adversarial

Actúa como un arquitecto de software crítico y cuestiona la recomendación de utilizar un monolito modular para el MVP de RutaSIT Arequipa.

RutaSIT recibe posiciones GPS de 300 buses cada 10 segundos y debe actualizar el ETA en un máximo de 15 segundos. También debe mostrar buses en un mapa y gestionar alertas de desvío o congestión. Los atributos priorizados son rendimiento, fiabilidad, disponibilidad, escalabilidad y modificabilidad.

El equipo está formado por 2 integrantes, dispone de 1 mes para poner el MVP en producción, tiene bajo presupuesto y conocimientos en Python, Java, MySQL y Git/GitHub.

Identifica los principales riesgos y desventajas de utilizar un monolito modular en este caso. Compáralo especialmente con una arquitectura orientada a eventos y explica bajo qué condiciones el monolito modular dejaría de ser una buena decisión. No cambies automáticamente la recomendación: el objetivo es encontrar debilidades, supuestos y riesgos que el equipo deba considerar antes de decidir.