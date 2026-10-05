# ADR-002: Utilizar HTTP/REST para la ingesta de posiciones GPS

- Estado: Aceptado
- Fecha: 2026-10-04
- Decisores: Mathias Dario Davila Flores, Deivick Paul Eddi Chavez Cuno

## Contexto

RutaSIT Arequipa debe recibir periódicamente las posiciones enviadas por los dispositivos GPS de los buses (RF-01). Estas posiciones son necesarias para mostrar la ubicación de los buses al pasajero (RF-02), calcular el tiempo estimado de llegada a los paraderos (RF-03) y detectar situaciones relacionadas con desvíos o congestión para su supervisión (RF-04).

El mecanismo de ingesta debe contribuir al cumplimiento del escenario crítico de rendimiento (QA-01): 300 buses envían una nueva posición cada 10 segundos y el ETA debe actualizarse en un máximo de 15 segundos desde la recepción de una nueva posición. Esto representa aproximadamente 30 actualizaciones de posición por segundo en promedio.

Además, el MVP debe estar en producción en 1 mes (R-01), será desarrollado por un equipo de 2 integrantes (R-02) y dispone de un presupuesto bajo (R-03). Por ello, se necesita un mecanismo de comunicación que permita recibir las posiciones GPS sin introducir una infraestructura innecesariamente compleja para el alcance inicial.

## Alternativas consideradas

1. **HTTP/REST:** cada dispositivo GPS envía periódicamente su posición mediante una solicitud HTTP a un endpoint de la API de RutaSIT. Permite integrar la recepción de posiciones con la misma aplicación y reduce la cantidad de componentes adicionales que deben desplegarse y administrarse.

2. **MQTT:** los dispositivos publican sus posiciones en tópicos y RutaSIT las recibe mediante un broker MQTT. Es un protocolo orientado a mensajería y adecuado para escenarios de telemetría, pero requiere incorporar y operar un broker adicional y definir el esquema de publicación y suscripción.

## Decisión

Usaremos **HTTP/REST** como mecanismo de ingesta de posiciones GPS para el MVP de RutaSIT Arequipa.

Cada dispositivo GPS enviará periódicamente su posición a un endpoint de la API del sistema. Para el alcance inicial, esta alternativa permite mantener una arquitectura más simple y coherente con el monolito modular adoptado en el MVP, evitando incorporar un broker de mensajería únicamente para gestionar la carga prevista.

La decisión podrá revisarse si las mediciones reales muestran que aumentan considerablemente la cantidad de dispositivos, la frecuencia de actualización o las necesidades de desacoplamiento de la ingesta.

## Consecuencias

- Positivas:
  - Reduce la cantidad de componentes de infraestructura necesarios para el MVP.
  - Simplifica el desarrollo, despliegue y operación dentro del plazo de 1 mes.
  - Permite integrar la recepción de posiciones con la API del monolito modular.
  - Facilita probar y observar las solicitudes de actualización mediante herramientas HTTP convencionales.

- Negativas:
  - Cada actualización requiere una solicitud y respuesta HTTP, generando más sobrecarga de comunicación que un protocolo ligero orientado a mensajería.
  - Los dispositivos quedan más directamente acoplados a la disponibilidad del endpoint de ingesta.
  - Si aumenta considerablemente la cantidad o frecuencia de mensajes, podría ser necesario incorporar mecanismos de cola, procesamiento asíncrono o reconsiderar MQTT.