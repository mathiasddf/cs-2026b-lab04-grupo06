# ISSUE-03: Falla con un GPS sin datos o trama incompleta

- **Reportado por:** Equipo de Integración de Telemetría RutaSIT Arequipa (Proveedores Conecta y TransCayma)
- **Módulo afectado:** `src/consultas/proveedores_gps.py` (`normalizar_trama_gps`, `DatosGPSIncompletosError`)

## Observado

Cuando un proveedor GPS de Conecta o TransCayma envía una trama vacía (`{}`), un valor nulo (`None`) o un diccionario con coordenadas o velocidad ausentes o en `None` (por ejemplo, `{"lat": -16.39, "lon": None, "velocidad": 25.0}`), la función `normalizar_trama_gps(trama: dict | None) -> LecturaGPS` intenta indexar directamente `trama["lat"]`, `trama["lon"]` y `trama["velocidad"]` y convertirlos a `float`.

Esto provoca excepciones no controladas (`TypeError`, `KeyError` o `AttributeError`) que interrumpen el flujo de procesamiento de telemetría en lugar de ser capturadas como un error de dominio conocido.

## Esperado

Contrato exacto de `normalizar_trama_gps(trama: dict | None) -> LecturaGPS`:

1. Si `trama` es un diccionario válido con valores numéricos no nulos en `"lat"`, `"lon"` y `"velocidad"`, debe retornar un objeto `LecturaGPS` normalizado (usando `antiguedad_seg=0` y `en_corredor=True` por defecto si las claves opcionales no están presentes o son `None`).
2. Si `trama` es `None`, no es un `dict`, está vacía (`{}`), le falta alguna clave obligatoria (`"lat"`, `"lon"`, `"velocidad"`), o alguno de esos campos es `None` o no convertible a número, debe lanzar explícitamente la excepción de dominio `DatosGPSIncompletosError` (subclase de `ValueError`) con un mensaje descriptivo, sin colapsar por `KeyError`, `TypeError` ni `AttributeError`.

## Prueba que reproduce el error

```bash
pytest tests/test_issue_03.py::test_issue_03_maneja_gps_sin_datos
```
