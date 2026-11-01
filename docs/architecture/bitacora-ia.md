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


# Bitácora de Uso Crítico de IA en el Diseño Arquitectónico — Laboratorio 08 (RutaSIT Arequipa)

> **Regla de oro aplicada:** *La IA propone, el equipo decide con evidencia. Ninguna táctica se adoptó sin un escenario prioritario, evidencia cuantitativa (simulación o fitness function) y su ADR.*

| # | Etapa / Prompt | Propuesta de la IA | Verificación del Equipo (Evidencia / Simulación / Restricciones) | Decisión Final |
|---|---|---|---|---|
| 1 | **E1 (Prompt IA 1 — Árbol de utilidad):** Generar escenarios de 6 partes para el paso de 300 a 1200 buses y 50 000 consultas en hora punta. | Propuso 7 escenarios y calificó `QA-05` (*cifrado en tránsito de las tramas GPS de los 1200 buses*) con prioridad **`(H,H)`** alegando alta complejidad criptográfica. | Verificamos la infraestructura actual: el proxy inverso Nginx del VPS ya termina TLS 1.3 (HTTPS) desde el MVP para 300 buses; pasar a 120 req/s de telemetría no requiere programar criptografía nueva. | **Corregida:** Se bajó la calificación de `QA-05` de `(H,H)` a **`(M,L)`** en `arbol.dot` para concentrar las iteraciones de ADD en `QA-01`, `QA-02`, `QA-03`, `QA-04` y `QA-06`. |
| 2 | **E2 (Prompt IA 2 — Tácticas para `QA-01`):** Proponer 4 conceptos de diseño para soportar 50 000 consultas/h con $\text{p95} \le 1500\text{ ms}$. | Recomendó como primera opción **migrar el monolito modular a 4 microservicios en Kubernetes con Apache Kafka** para procesar los 1200 buses. | Contrastamos contra `drivers.md` (1 mes de plazo y presupuesto de 1 VPS) y ejecutamos `fitness/rendimiento.py`: con índice en PostGIS + caché Redis (TTL 10 s), el monolito en 1 VPS logra un **$\text{p95} = 79.9\text{ ms}$** a $20\text{ req/s}$. | **Rechazada:** Sesgo de la IA hacia arquitecturas de moda (*hype*). Se mantuvo el Monolito Modular (`ADR-001` y `ADR-006`). |
| 3 | **E2 (Paso 4 — Afirmación sin evidencia sobre la caché):** Al evaluar las tácticas de rendimiento. | La IA afirmó que *"colocar una caché Redis delante de `consultar_eta` basta por sí sola para cumplir siempre el p95 sin necesidad de crear índices nuevos en PostgreSQL"*. | Trazamos la **curva de sensibilidad** en `fitness/rendimiento.py` variando la tasa de aciertos de 0% a 95% a $20\text{ req/s}$: sin el índice en BD, cuando la tasa de aciertos baja del **35%** (ej. tras un reinicio de Redis), el $\text{p95}$ supera los $1500\text{ ms}$ y llega a **$18\,078.7\text{ ms}$**. | **Corregida:** Se adoptaron **ambas tácticas** (Índice compuesto + Caché Redis TTL 10 s), logrando $141.7\text{ ms}$ incluso con 0% de aciertos en caché (`ADR-006`). |
| 4 | **E4 (Iteración 2 — Disponibilidad `QA-02`):** Diseñar el fallback de última ubicación cuando cae el SDK GPS de una concesionaria por 15 minutos. | Propuso implementar el Circuit Breaker guardando la última posición conocida de cada bus **únicamente en Redis en memoria (sin persistencia)** para responder durante la caída. | Realizamos análisis de modos de falla: si Redis se reinicia o desaloja llaves por memoria mientras el SDK de ConectaAQP está caído, se pierde la posición de los 1200 buses (**Riesgo R3**). | **Corregida:** Se implementó `RepositorioUltimaPosicion` respaldado en una **tabla persistente de PostgreSQL/PostGIS** (`ADR-007`), logrando 0 consultas perdidas en `fitness/disponibilidad.py`. |
| 5 | **E4 (Iteración 3 — Seguridad multiconcesionaria `QA-04`):** Aislar los datos de las 8 empresas concesionarias del SIT. | Sugirió crear **una instancia de base de datos PostgreSQL separada por cada empresa concesionaria** para garantizar aislamiento físico. | Evaluamos el impacto en `QA-01` y `QA-06`: cuando un pasajero consulta un paradero de la Av. Ejército por donde pasan 4 empresas, el backend tendría que consultar y unir 4 bases de datos distintas, degradando la latencia y complicando las migraciones en un solo VPS. | **Rechazada:** Se adoptó tabla unificada con columna `concesionaria_id` + **Row-Level Security (RLS)** + claim en el JWT (`ADR-008`), protegido con `test_ff06`. |
| 6 | **E3 / E7 (Prompt IA 3 — Evaluador adversario ATAM-lite):** Identificar riesgos críticos en la arquitectura de RutaSIT 2.0. | **Falso positivo detectado:** La IA reportó como riesgo crítico que *"el protocolo SSE (`ADR-003`) y el worker de ingesta colapsarán porque 1200 buses generan un tráfico inmanejable para un servidor Python"*. | Calculamos la carga real: $1200\text{ buses} / 10\text{ s} = 120\text{ escrituras cortas/s}$, y el flujo hacia los paraderos es 100% unidireccional (servidor $\rightarrow$ cliente), donde SSE sobre HTTP/2 multiplexa conexiones con mínimo consumo de RAM. Se pidió a la IA el cálculo que sustentaba su alerta y reconoció no haber dividido entre el intervalo de 10 s. | **Rechazada (Falso Positivo refutado con números)** y documentado en `atam-lite.md`. |
