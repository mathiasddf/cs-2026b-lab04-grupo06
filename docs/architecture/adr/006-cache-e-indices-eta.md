# ADR-006: Adopción de Índices Compuestos en PostgreSQL y Capa de Caché en Redis para QA-01

- **Estado:** Aceptado
- **Fecha:** Octubre 2026
- **Contexto:** Iteración 1 de ADD (Lab 08) — Escenario QA-01 (50 000 consultas de ETA/h con 1200 buses activos en hora punta).

## Contexto y Problema
En hora punta (pico de 20 req/s), la consulta de cálculo de ETA colapsa el servidor VPS único (4 workers) alcanzando un p95 de 18 078.7 ms debido a escaneos secuenciales sobre la tabla de telemetría de 1200 buses (`telemetria_gps`). Esto viola el presupuesto de latencia de QA-01 (p95 <= 1500 ms).

## Decisión
Se implementan de manera conjunta dos tácticas de arquitectura:
1. **Gestionar Recursos (BD):** Creación de un índice compuesto B-Tree `(bus_id, reportado_en DESC)` y vistas espaciales en PostGIS.
2. **Controlar la Demanda (Caché):** Instanciación de Redis 7 como caché en memoria para las respuestas de ETA indexadas por clave `eta:{paradero_id}:{ruta_id}:{modo}` con un TTL de 10 segundos.

## Consecuencias y Trade-offs
- **Positivas:**
  - El p95 en pico de 20 req/s se reduce de 18 078.7 ms a 79.9 ms (reducción del 99.5%), cumpliendo holgadamente QA-01.
  - Se mantiene la arquitectura de Monolito Modular en un único VPS sin incurrir en costos de balanceadores ni nodos adicionales (cumple R-01 y R-03).
  - Resiliencia ante falla de caché: con 0% de aciertos en Redis (caché fría), el índice en BD mantiene el p95 en 141.7 ms (< 1500 ms).
- **Negativas / Riesgos:**
  - El tiempo estimado de llegada puede tener un desfase máximo de hasta 10 segundos respecto a la posición física exacta del bus (aceptable, dado que la telemetría se reporta en intervalos de 10 s).
  - Ligero incremento en el uso de disco e impacto marginal (+3% CPU) durante las escrituras de telemetría por mantenimiento del índice.