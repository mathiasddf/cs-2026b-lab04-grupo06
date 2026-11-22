# ISSUE-02: Desvío no detectado en curvas del corredor

- **Reportado por:** Centro de Control RutaSIT Arequipa (Concesionaria TransCayma — Curva Av. Ejército → Av. Cayma)
- **Módulo afectado:** `src/consultas/estados.py` (`esta_en_corredor_curva`)

## Observado

Al verificar si un bus de TransCayma permanece dentro del corredor autorizado en un tramo con curva en "L" (por ejemplo, el giro desde Av. Ejército hacia Av. Cayma definido por la polilínea `[(-16.3900, -71.5450), (-16.3900, -71.5350), (-16.3800, -71.5350)]`), la función `esta_en_corredor_curva(posicion, puntos_ruta, tolerancia=0.002)` únicamente comprueba si la coordenada `(lat, lon)` del bus cae dentro del rectángulo envolvente (*bounding box* min/max de latitud y longitud) de los puntos de la ruta.

Como resultado, cuando el bus corta camino o se desvía hacia calles interiores fuera de la curva (p. ej., `(-16.3820, -71.5430)`, a `0.008` grados / ~880 m de los segmentos reales del corredor), el sistema lo marca erróneamente como `True` (`en_corredor=True`) y nunca dispara la transición a `DESVIADO`.

## Esperado

Contrato exacto de `esta_en_corredor_curva(posicion: tuple[float, float], puntos_ruta: list[tuple[float, float]], tolerancia: float = 0.002) -> bool`:

1. Debe calcular la **distancia euclidiana mínima** desde `posicion` hasta cada segmento consecutivo `(puntos_ruta[i], puntos_ruta[i + 1])` de la polilínea del corredor (o al único punto si la ruta tiene 1 punto; si `puntos_ruta` está vacía, retorna `False`).
2. Debe retornar `True` únicamente si esa distancia mínima es menor o igual a `tolerancia` (por defecto `0.002` grados, equivalente aprox. a ~200 m).
3. Si la distancia mínima a todos los segmentos de la curva excede `tolerancia`, debe retornar `False` para permitir que el servicio marque el viaje como `DESVIADO`.

## Prueba que reproduce el error

```bash
pytest tests/test_issue_02.py::test_issue_02_detecta_desvio_en_curva
```
