# Drivers arquitectónicos — RutaSIT Arequipa

## 1. Requisitos funcionales clave

| ID | Requisito | Actor | Prioridad |
|---|---|---|---|
| RF-01 | El bus envía periódicamente su ubicación geográfica al sistema mediante GPS. | Bus (GPS) | Alta |
| RF-02 | El pasajero consulta la ubicación actual de los buses sobre un mapa. | Pasajero | Alta |
| RF-03 | El pasajero consulta el tiempo estimado de llegada de los buses a un paradero. | Pasajero | Alta |
| RF-04 | El sistema identifica situaciones de desvío o congestión que afectan las rutas. | Operador | Alta |
| RF-05 | El pasajero recibe alertas sobre desvíos o congestión que afecten el servicio. | Pasajero | Alta |
| RF-06 | El operador supervisa la ubicación y el estado de los buses para dar seguimiento al servicio. | Operador | Media |

## 2. Atributos de calidad (ordenados por prioridad)

1. **Rendimiento** — Es el atributo crítico porque el sistema debe procesar las posiciones enviadas por 300 buses cada 10 segundos y actualizar el tiempo estimado de llegada (ETA) en un máximo de 15 segundos.

2. **Fiabilidad** — La información de ubicación, tiempos estimados de llegada y alertas debe mantenerse correcta y consistente para evitar información errónea durante la operación del servicio.

3. **Disponibilidad** — El sistema debe permanecer accesible para que pasajeros y operadores puedan consultar la información de los buses durante los periodos de funcionamiento del transporte.

4. **Escalabilidad** — La arquitectura debe permitir soportar un crecimiento en la cantidad de buses, posiciones recibidas y usuarios concurrentes sin degradar significativamente el rendimiento.

5. **Modificabilidad** — Los cambios en rutas, reglas de cálculo y funcionalidades deben poder incorporarse sin requerir modificaciones extensas en todo el sistema.

## 3. Restricciones

| ID | Tipo | Restricción |
|---|---|---|
| R-01 | Plazo | El MVP debe estar en producción en un plazo máximo de 1 mes. |
| R-02 | Equipo | El equipo está conformado por 2 integrantes con conocimientos en Python, Java, MySQL y Git/GitHub. |
| R-03 | Presupuesto | El proyecto dispone de un presupuesto bajo, por lo que se priorizarán tecnologías de código abierto y servicios gratuitos o de bajo costo. |
| R-04 | Tecnología | La solución debe priorizar tecnologías conocidas por el equipo y evitar una infraestructura excesivamente compleja que dificulte su desarrollo y operación dentro del plazo establecido. |

## 4. Escenarios de atributos de calidad

| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
|---|---|---|---|---|---|---|---|
| QA-01 | Rendimiento | 300 buses con GPS | Cada bus envía una nueva posición geográfica cada 10 segundos. | Operación normal del servicio | Módulo de recepción de posiciones y cálculo de ETA | El sistema recibe y procesa las posiciones y actualiza los tiempos estimados de llegada. | El ETA debe actualizarse en un tiempo máximo de 15 segundos desde la recepción de la nueva posición. |
| QA-02 | Disponibilidad | Pasajero | Solicita consultar la ubicación de los buses y los tiempos estimados de llegada. | Durante el horario de operación del servicio | Aplicación y servicios de consulta de RutaSIT | El sistema mantiene disponible la información necesaria para atender la consulta. | Disponibilidad mensual mínima del 99 %. |
| QA-03 | Fiabilidad | Bus con GPS | Envía actualizaciones sucesivas de su posición geográfica. | Operación normal con recepción continua de posiciones | Módulo de procesamiento y almacenamiento de ubicaciones | El sistema registra las actualizaciones válidas y mantiene la posición más reciente de cada bus para las consultas y cálculos de ETA. | Al menos el 99 % de las posiciones válidas recibidas deben ser procesadas y registradas correctamente. |