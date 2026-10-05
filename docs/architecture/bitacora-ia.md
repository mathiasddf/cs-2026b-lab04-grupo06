# Bitácora de uso de IA — RutaSIT Arequipa

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 04/10/2026 | ChatGPT | Proponer tres alternativas arquitectónicas para RutaSIT considerando los drivers, el plazo, el equipo y el presupuesto. | Propuso monolito modular, arquitectura orientada a eventos y microservicios, recomendando el monolito modular para el MVP. | Se contrastaron las alternativas con QA-01, R-01, R-02 y R-03. La recomendación se mantuvo como candidata hasta evaluarla mediante la matriz de decisión. | Aceptada |
| 2 | 04/10/2026 | ChatGPT | Realizar una crítica adversarial de la recomendación de utilizar un monolito modular. | Identificó riesgos relacionados con escalabilidad, procesamiento síncrono, aislamiento de fallos y crecimiento futuro, destacando ventajas de una arquitectura orientada a eventos. | Se calculó que 300 buses enviando una posición cada 10 segundos representan aproximadamente 30 actualizaciones/s. Se determinó que esta cifra por sí sola no demuestra la necesidad de una arquitectura distribuida, pues también influyen la complejidad del cálculo de ETA, usuarios concurrentes e infraestructura disponible. | Corregida |
| 3 | 04/10/2026 | ChatGPT | Revisar la organización de los módulos del diagrama Mermaid tomando como referencia el ejemplo proporcionado en la guía. | Propuso representar los cinco módulos funcionales al mismo nivel para obtener un diagrama más limpio y similar al ejemplo del profesor. | Se revisaron las dependencias de RutaSIT y se determinó que Ubicaciones y Rutas y buses proporcionan información necesaria para ETA y Alertas. Se decidió conservar estas dependencias en lugar de modificar la arquitectura solo para asemejarla visualmente al ejemplo. | Rechazada |
| 4 | 04/10/2026 | ChatGPT | Determinar dos decisiones arquitectónicas adicionales para los ADR de RutaSIT. | Propuso inicialmente documentar la elección entre una base de datos relacional y documental. Posteriormente se analizaron decisiones sobre ingesta GPS y actualización en tiempo real. | Se verificó su relación con los drivers. Aunque la persistencia era una decisión válida, se consideró menos representativa del problema crítico de RutaSIT. Se priorizaron el protocolo de ingesta GPS y el mecanismo de actualización al pasajero. | Corregida |
| 5 | 04/10/2026 | ChatGPT | Comparar alternativas para la ingesta GPS y la actualización de información hacia los pasajeros. | Para la ingesta comparó HTTP/REST y MQTT; para las actualizaciones comparó Polling HTTP, SSE y WebSocket. Propuso HTTP/REST y SSE para el MVP. | Se contrastaron las alternativas con RF-01, RF-02, RF-03, QA-01, R-01, R-02 y R-03. Se verificó que las elecciones reducen infraestructura adicional y se ajustan a las necesidades del MVP, manteniendo la posibilidad de revisarlas si cambian los requisitos. | Aceptada |
| 6 | 04/10/2026 | ChatGPT | Generar en PlantUML la segunda mejor alternativa arquitectónica de la matriz de decisión. | Propuso una arquitectura orientada a eventos con recepción GPS, broker de eventos y componentes para ubicaciones, rutas, ETA, alertas y consultas. | Se verificó que la arquitectura orientada a eventos era efectivamente la segunda mejor alternativa, con 4.00/5 frente a 4.25/5 del monolito modular. El código se validó en PlantUML y se exportó la imagen. | Aceptada |
| 7 | 04/10/2026 | ChatGPT | Diseñar la vista de despliegue de RutaSIT mediante Python Diagrams. | Propuso representar pasajeros, operador, buses/GPS, Internet, Nginx, aplicación RutaSIT, base de datos, monitoreo y servicio externo de mapas. | Se comprobó la coherencia con los ADR y se realizó una verificación técnica ejecutando el script con Python Diagrams y Graphviz. La ejecución generó correctamente la imagen despliegue.png. | Aceptada |

## Anexo: prompts completos

### Prompt 1

Actúa como arquitecto de software y propón 3 alternativas de estilo arquitectónico para el MVP de RutaSIT Arequipa, un sistema de seguimiento en tiempo real de buses.

El sistema debe permitir consultar la ubicación de buses en un mapa, calcular el tiempo estimado de llegada (ETA) a los paraderos, gestionar alertas de desvío o congestión y permitir la supervisión del servicio. Como requisito crítico de rendimiento, 300 buses con GPS envían su posición cada 10 segundos y el ETA debe actualizarse en un máximo de 15 segundos.

Los atributos de calidad priorizados son rendimiento, fiabilidad, disponibilidad, escalabilidad y modificabilidad. El MVP debe estar en producción en 1 mes, el equipo está formado por 2 integrantes con conocimientos en Python, Java, MySQL y Git/GitHub, y el presupuesto es bajo, por lo que deben priorizarse soluciones de código abierto o de bajo costo. Además, el sistema depende de los datos de ubicación proporcionados por los dispositivos GPS de los buses.

Propón exactamente 3 alternativas de estilo arquitectónico viables. Para cada una, explica en 2 o 3 líneas cómo se organizaría el sistema y señala brevemente sus principales ventajas y desventajas para estos drivers. Finalmente, recomienda una de las tres alternativas para este MVP y justifica la recomendación. La recomendación será evaluada posteriormente por el equipo y no se asumirá como decisión definitiva.

### Prompt 2

Actúa como un arquitecto de software crítico y cuestiona la recomendación de utilizar un monolito modular para el MVP de RutaSIT Arequipa.

RutaSIT recibe posiciones GPS de 300 buses cada 10 segundos y debe actualizar el ETA en un máximo de 15 segundos. También debe mostrar buses en un mapa y gestionar alertas de desvío o congestión. Los atributos priorizados son rendimiento, fiabilidad, disponibilidad, escalabilidad y modificabilidad.

El equipo está formado por 2 integrantes, dispone de 1 mes para poner el MVP en producción, tiene bajo presupuesto y conocimientos en Python, Java, MySQL y Git/GitHub.

Identifica los principales riesgos y desventajas de utilizar un monolito modular en este caso. Compáralo especialmente con una arquitectura orientada a eventos y explica bajo qué condiciones el monolito modular dejaría de ser una buena decisión. No cambies automáticamente la recomendación: el objetivo es encontrar debilidades, supuestos y riesgos que el equipo deba considerar antes de decidir.

### Prompt 3

Revisa la organización del diagrama Mermaid de RutaSIT Arequipa tomando como referencia un ejemplo de monolito modular en el que los módulos funcionales aparecen al mismo nivel.

Determina si conviene representar también de forma independiente los módulos Ubicaciones, Rutas y buses, Cálculo de ETA, Alertas y Consultas, o si deben conservarse las dependencias existentes entre ellos. La prioridad es que el diagrama represente correctamente la arquitectura de RutaSIT y no solamente que se parezca visualmente al ejemplo proporcionado.

### Prompt 4

Analiza qué decisiones arquitectónicas adicionales son realmente relevantes para RutaSIT Arequipa además de la elección del estilo arquitectónico.

Considera alternativas relacionadas con persistencia de datos, protocolo de ingesta de posiciones GPS y mecanismo de actualización de información hacia los pasajeros. RutaSIT recibe posiciones de 300 buses cada 10 segundos, debe actualizar el ETA en un máximo de 15 segundos, dispone de 1 mes para desarrollar el MVP, tiene un equipo de 2 integrantes y un presupuesto bajo.

Determina cuáles de estas decisiones tienen mayor impacto arquitectónico para el caso y justifica la selección.

### Prompt 5

Evalúa las alternativas de comunicación para dos necesidades de RutaSIT Arequipa.

Primero, compara HTTP/REST y MQTT como mecanismos para recibir periódicamente las posiciones enviadas por los dispositivos GPS de los buses.

Segundo, compara Polling HTTP, Server-Sent Events (SSE) y WebSocket para entregar al pasajero actualizaciones de ubicación, ETA y alertas.

Considera el requisito de 300 buses enviando posiciones cada 10 segundos, un ETA actualizado en un máximo de 15 segundos, un equipo de 2 integrantes, un plazo de 1 mes y un presupuesto bajo. Recomienda una alternativa para cada necesidad y explica sus consecuencias.

### Prompt 6

Genera un diagrama de componentes en PlantUML para representar la segunda mejor alternativa arquitectónica de RutaSIT Arequipa.

La matriz de decisión obtuvo los siguientes resultados: monolito modular 4.25/5, arquitectura orientada a eventos 4.00/5 y microservicios 3.45/5. Por lo tanto, representa la arquitectura orientada a eventos como alternativa descartada.

Incluye recepción de posiciones GPS, broker de eventos, componentes para ubicaciones, rutas y buses, cálculo de ETA, alertas y consultas, base de datos, actores principales y servicio externo de mapas. Agrega una nota de 3 a 5 líneas que explique por qué se descartó la alternativa y cite su puntuación de 4.00/5.

### Prompt 7

Diseña una vista de despliegue para RutaSIT Arequipa utilizando Python Diagrams y Graphviz.

Representa los dispositivos y usuarios del sistema, incluyendo pasajeros, operador y buses con GPS; comunicación mediante Internet; un proxy; la aplicación RutaSIT; base de datos; monitoreo y un servicio externo de mapas.

Utiliza Cluster para agrupar los elementos desplegados en el servidor y Edge con etiquetas para identificar las conexiones. El despliegue debe ser coherente con las decisiones arquitectónicas tomadas: monolito modular, ingesta de posiciones GPS mediante HTTP/REST y actualizaciones hacia los pasajeros mediante SSE.