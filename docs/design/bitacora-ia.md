# Bitácora de uso de IA — RutaSIT Arequipa (Laboratorio 05)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 10/10/2026 | Gemini | Generar el diagrama de clases en PlantUML para el entregable E1 basado en el ADR-001 (monolito modular) y la historia de usuario de consulta de ETA. | Propuso las entidades clave (`Bus`, `Ruta`, `Paradero`, `Viaje`, `PosicionGPS`), una enumeración y un servicio base de ubicaciones. | Se revisó la lista de verificación: se aseguraron multiplicidades explícitas en ambos extremos de todas las asociaciones, se tiparon los atributos con visibilidad y se estructuró el puerto `ServicioMapasExterno`. | Aceptada |

## Anexo: prompts completos

### Prompt 1 (E1: Diagrama de Clases)

Actúa como un Arquitecto de Software experto. Basándote en la decisión tomada en nuestro ADR-001 de usar un monolito modular para *RutaSIT Arequipa* (enfocado en procesar 300 buses cada 10 segundos y calcular el ETA en menos de 15 segundos) y en la historia de usuario sobre la consulta de la ubicación y ETA del bus, genera un diagrama de clases en PlantUML que represente los módulos internos (ubicaciones, rutas, buses y cálculo de ETA), incluyendo al menos 6 clases, 1 interfaz como puerto hacia servicios externos (como mapas), una enumeración para los estados del bus, y atributos tipados con visibilidad.