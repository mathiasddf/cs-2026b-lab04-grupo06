# ADR-007: Resiliencia ante caída de proveedores GPS con Circuit Breaker, Last-Known en PostgreSQL y PWA Offline-first

- **Estado:** Aceptado
- **Fecha:** 29/10/2026
- **Decisores:** Chavez Cuno Deivick Paul Eddi, Davila Flores Mathias Dario
- **Escenarios atendidos:** QA-02 (Caída de SDK GPS por 15 min $\rightarrow$ 0 errores HTTP 500) y QA-03 (Corte de señal móvil del pasajero por 3 min)

## Contexto
En el Laboratorio 07 implementamos el decorador `ConReintentosGPS` (3 intentos ante `TimeoutError`). Sin embargo, la evaluación ATAM-lite (E3) y la simulación Monte Carlo (`fitness/disponibilidad.py`) evidenciaron que durante una caída sostenida de 15 minutos del SDK GPS de una concesionaria, hacer 3 reintentos por cada consulta genera 1200 llamadas fallidas contra el proveedor caído, reteniendo los workers del VPS y devolviendo 400 respuestas sin posición válida. Además, la propuesta inicial de la IA de guardar la última posición solo en Redis volátil introducía el riesgo de perder toda la flota si Redis se reiniciaba (Riesgo R3).

## Alternativas consideradas
1. **Mantener solo reintentos simples (`ConReintentosGPS` del Lab 07):** Rechazada para caídas largas porque triplica la carga sobre el proveedor caído y falla en 400 de 2400 consultas.
2. **Guardar la última posición conocida únicamente en Redis (propuesto por la IA):** Rechazada porque un reinicio de Redis durante la caída del proveedor dejaría sin posición a los 1200 buses.
3. **Combinar Reintentos cortos + ConCircuitBreakerGPS (Decorator) + tabla persistente `ultima_posicion_bus` en PostgreSQL + PWA Offline-first con IndexedDB:** Abre el circuito tras 3 fallas consecutivas durante 60 s y sirve la última ubicación válida persistida en disco indicando la antigüedad.

## Decisión
Adoptaremos dos mecanismos de disponibilidad complementarios:
1. En el backend (`src/consultas/resiliencia.py`), envolver los adaptadores `ProveedorGPS` con `ConCircuitBreakerGPS` respaldado por la tabla `ultima_posicion_bus` en PostgreSQL/PostGIS.
2. En el frontend móvil (PWA Pasajero), almacenar en IndexedDB mediante un Service Worker el trazado de la ruta activa y el último evento SSE para mostrarlos en $\le 200\text{ ms}$ sin señal y reconectar con `Last-Event-ID` en $\le 5\text{ s}$ (QA-03).

## Consecuencias y Trade-off aceptado
- **Positivas (+):** La simulación Monte Carlo demuestra 0 consultas fallidas (100% de disponibilidad) y reduce las llamadas al proveedor caído de 1200 a 32 (-97.3%).
- **Negativas / Trade-off aceptado (-):** Se acepta consistencia eventual / precisión degradada durante los minutos que dure la caída del operador GPS: el pasajero recibe un ETA proyectado a partir de la última velocidad y posición conocidas junto con un aviso explícito de antigüedad de señal.