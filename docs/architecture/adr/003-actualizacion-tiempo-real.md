# ADR-003: Utilizar Server-Sent Events para actualizaciones en tiempo real

- Estado: Aceptado
- Fecha: 2026-10-04
- Decisores: Mathias Dario Davila Flores, Deivick Paul Eddi Chavez Cuno

## Contexto

RutaSIT Arequipa debe permitir al pasajero consultar la ubicación de los buses en el mapa (RF-02), visualizar el tiempo estimado de llegada a los paraderos (RF-03) y recibir información actualizada relacionada con alertas del servicio (RF-05).

Estos datos cambian conforme RutaSIT recibe nuevas posiciones GPS. El mecanismo utilizado para entregar las actualizaciones al cliente debe contribuir al cumplimiento del escenario crítico de rendimiento (QA-01), donde 300 buses envían posiciones cada 10 segundos y el ETA debe actualizarse en un máximo de 15 segundos desde la recepción de una nueva posición.

El MVP debe estar en producción en 1 mes (R-01), será desarrollado por un equipo de 2 integrantes (R-02) y dispone de un presupuesto bajo (R-03). Por ello, se requiere un mecanismo que permita enviar actualizaciones frecuentes al pasajero sin introducir una solución de comunicación más compleja de lo necesario.

## Alternativas consideradas

1. **Polling HTTP:** el cliente consulta periódicamente al servidor para comprobar si existen nuevas posiciones, ETA o alertas. Es sencillo de implementar, pero genera solicitudes incluso cuando no existen cambios y la frecuencia de consulta condiciona qué tan rápido se refleja una actualización.

2. **Server-Sent Events (SSE):** el cliente mantiene una conexión HTTP mediante la cual el servidor puede enviar nuevas actualizaciones cuando estén disponibles. Se adapta al flujo principalmente unidireccional de RutaSIT, desde el servidor hacia el pasajero.

3. **WebSocket:** mantiene un canal de comunicación bidireccional entre cliente y servidor. Permite intercambio de mensajes en ambos sentidos, pero incorpora capacidades y complejidad que no son necesarias para el flujo principal de actualización del MVP.

## Decisión

Usaremos **Server-Sent Events (SSE)** para enviar al cliente las actualizaciones de ubicación, ETA y alertas que deban reflejarse durante el seguimiento de los buses.

Se elige SSE porque RutaSIT necesita principalmente distribuir información desde el servidor hacia los pasajeros. Permite mantener una conexión para entregar nuevos datos sin realizar consultas HTTP periódicas y evita introducir comunicación bidireccional permanente cuando el MVP no la requiere.

Las operaciones iniciadas por el usuario, como las consultas convencionales a la aplicación, continuarán realizándose mediante HTTP. La decisión podrá revisarse si en futuras versiones aparecen requisitos que necesiten intercambio bidireccional continuo entre cliente y servidor.

## Consecuencias

- Positivas:
  - Permite que el servidor envíe actualizaciones al cliente cuando existan nuevos datos.
  - Evita realizar solicitudes periódicas de polling cuando no existen cambios.
  - Se ajusta al flujo principalmente unidireccional de ubicación, ETA y alertas hacia el pasajero.
  - Utiliza comunicación basada en HTTP y evita incorporar un canal bidireccional cuando no es necesario para el MVP.

- Negativas:
  - Mantiene conexiones HTTP abiertas mientras el pasajero utiliza el seguimiento en tiempo real.
  - No proporciona comunicación bidireccional completa como WebSocket.
  - El servidor deberá administrar las conexiones activas de los clientes.
  - Si en el futuro aparecen funcionalidades que requieran intercambio bidireccional continuo, será necesario reevaluar esta decisión.