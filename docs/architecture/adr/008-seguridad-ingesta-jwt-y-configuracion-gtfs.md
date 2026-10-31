# ADR-008: Aislamiento multiconcesionaria con JWT + Row-Level Security (RLS) y configuración de rutas en PostGIS

- **Estado:** Aceptado
- **Fecha:** 30/10/2026
- **Decisores:** Chavez Cuno Deivick Paul Eddi, Davila Flores Mathias Dario
- **Escenarios atendidos:** QA-04 (Aislamiento de telemetría entre concesionarias) y QA-06 (Actualización de rutas y desvíos en $\le 2\text{ h}$ sin desplegar código)

## Contexto
Al escalar de 300 a 1200 buses operados por múltiples empresas concesionarias del SIT Arequipa, debemos impedir que un operador manipule o consulte unidades de otra empresa (QA-04) sin fragmentar la base de datos que alimenta las consultas unificadas de los pasajeros. Asimismo, las frecuentes obras viales en Arequipa exigen modificar corredores y desvíos sin recompilar ni redesplegar el monolito (QA-06).

## Alternativas consideradas
1. **Una base de datos o un esquema por concesionaria:** Rechazada porque complica las consultas espaciales de un paradero donde confluyen varias empresas y multiplica el mantenimiento de migraciones en un único VPS.
2. **Columna `concesionaria_id` + Políticas Row-Level Security (RLS) en PostgreSQL + Claim `concesionaria_id` en el JWT del operador + Tablas GTFS/PostGIS de configuración de rutas:** Aísla relacional y criptográficamente a cada operador manteniendo una sola tabla indexada para lecturas de pasajeros, y difiere el enlace de los trazados viales a la base de datos.

## Decisión
1. Autenticar la ingesta y el panel de cada empresa concesionaria mediante tokens JWT que incluyan el claim `concesionaria_id`, validándolo en la aplicación y mediante políticas Row-Level Security (RLS) en PostgreSQL (QA-04).
2. Almacenar los segmentos de ruta, paraderos y polígonos de desvíos activos en tablas PostGIS compatibles con GTFS editables desde el Panel de Operador SIT sin desplegar código (QA-06).

## Consecuencias y Trade-off aceptado
- **Positivas (+):** Incorporar una nueva concesionaria o aplicar un desvío municipal por obras toma menos de 15 minutos mediante configuración en base de datos, con 0 fugas de datos verificadas por la fitness function `test_ff06`.
- **Negativas / Trade-off aceptado (-):** Un error humano al configurar las políticas RLS o al dibujar un polígono de desvío en BD podría afectar las consultas (Riesgo R2), por lo que se mitiga obligatoriamente con la fitness function `test_ff06` en CI y validación geométrica previa al guardado.