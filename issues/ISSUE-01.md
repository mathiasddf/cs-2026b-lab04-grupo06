# ISSUE-01: Tiempo de llegada (ETA) negativo si el bus ya pasó el paradero

- **Reportado por:** Equipo de Operaciones SIT Arequipa (Concesionaria Conecta — Corredor Av. Ejército)
- **Módulo afectado:** `src/consultas/estrategias_eta.py` (`calcular_eta_a_paradero`)

## Observado

Al consultar el tiempo estimado de llegada (ETA) de una unidad de Conecta hacia un paradero de la Av. Ejército cuando el bus ya superó la ubicación kilométrica del paradero (`posicion_bus_km > posicion_paradero_km`), la función `calcular_eta_a_paradero(posicion_bus_km, posicion_paradero_km, velocidad_kmh, estrategia=None)` calcula una distancia restante negativa (`posicion_paradero_km - posicion_bus_km < 0`) y retorna un **ETA negativo** (por ejemplo, `-4.0` minutos cuando el bus está en el km `8.0`, el paradero en el km `6.0` y la velocidad es `30.0 km/h`).

Este valor negativo aparece directamente en las pantallas de paradero y confunde a los pasajeros.

## Esperado

Contrato exacto de `calcular_eta_a_paradero(posicion_bus_km: float, posicion_paradero_km: float, velocidad_kmh: float, estrategia: EstrategiaETA | None = None) -> float`:

1. Si el bus aún no llega al paradero (`posicion_bus_km < posicion_paradero_km`), calcula y retorna el ETA positivo en minutos (redondeado a 2 decimales) usando la estrategia recibida o `ETAFlujoLibre()` por defecto.
2. Si el bus ya alcanzó o superó el paradero (`posicion_bus_km >= posicion_paradero_km`), **nunca debe retornar un ETA negativo**: debe devolver exactamente `0.0` (indicando que el bus ya pasó o se encuentra en el paradero).

## Prueba que reproduce el error

```bash
pytest tests/test_issue_01.py::test_issue_01_eta_no_negativo_si_bus_paso_paradero
```
