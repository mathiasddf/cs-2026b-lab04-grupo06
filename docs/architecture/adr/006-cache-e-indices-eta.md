# ADR-006: Adopción de índice geoespacial compuesto y caché Redis con TTL de 10 s para cálculo de ETA

- **Estado:** Aceptado
- **Fecha:** 28/10/2026
- **Decisores:** Chavez Cuno Deivick Paul Eddi, Davila Flores Mathias Dario
- **Escenario atendido:** QA-01 (50 000 consultas de ETA en hora punta con 1200 buses $\rightarrow$ p95 $\le$ 1500 ms)

## Contexto
Con el crecimiento de RutaSIT Arequipa de 300 a 1200 buses y hasta 50 000 consultas de tiempo de llegada en hora punta (≈14 req/s sostenidos y picos de 20 req/s en paraderos troncales), la simulación de colas M/G/c (`fitness/rendimiento.py`) demostró que la arquitectura actual sin tácticas satura los 4 workers del VPS (utilización > 100%), elevando el p95 a 18 078.7 ms, incumpliendo por 12 veces la meta de 1500 ms.

## Alternativas consideradas
1. **Migrar a microservicios con Kafka y Kubernetes (propuesto por la IA):** Rechazada porque viola el plazo de 1 mes y el presupuesto de 1 VPS (`drivers.md`).
2. **Escalar vertical/horizontalmente a 8 workers (segundo VPS):** Reduce el p95 en pico a 491.3 ms, pero duplica el costo mensual de infraestructura; queda como Plan B.
3. **Crear solo caché en Redis sin optimizar la base de datos:** Cumple cuando la tasa de aciertos es alta (258.5 ms al 85%), pero la curva de sensibilidad reveló que por debajo del 35% de aciertos (o tras reiniciar Redis) el p95 supera los 1500 ms.
4. **Combinar índice compuesto (bus_id, reportado_en DESC) en PostgreSQL/PostGIS + caché de ETA por (paradero_id, ruta_id) en Redis con TTL = 10 s:** El índice garantiza el presupuesto incluso con caché fría (138.9 ms) y la caché reduce el p95 a 79.9 ms.

## Decisión
Mantendremos el Monolito Modular (ADR-001) en un solo VPS e implementaremos la combinación de:
1. Índice compuesto B-Tree `(bus_id, reportado_en DESC)` e índice espacial GiST en PostgreSQL/PostGIS.
2. Contenedor Redis para cachear el resultado de `consultar_eta` por `(paradero_id, ruta_id, modo_calculo)` con un TTL estricto de 10 segundos.

## Consecuencias y Trade-off aceptado
- **Positivas (+):** El p95 en pico de 20 req/s baja de 18 078.7 ms a 79.9 ms (-99.5%), soportando la campaña de 1200 buses sin aumentar el gasto mensual de servidor.
- **Negativas / Trade-off aceptado (-):** Se acepta un desfase máximo de frescura de hasta 10 segundos en el ETA mostrado a los pasajeros (Riesgo R4), lo cual es imperceptible dado que las unidades de transporte envían su trama GPS cada 10 segundos. Las escrituras en base de datos asumen un pequeño sobrecosto por mantenimiento de índices.