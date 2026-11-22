"""Pruebas del ISSUE-03: Falla con un GPS sin datos o trama incompleta."""
import pytest
from src.consultas.proveedores_gps import (
    DatosGPSIncompletosError,
    LecturaGPS,
    normalizar_trama_gps,
)


def test_issue_03_caso_normal_trama_completa():
    """Caso feliz: una trama GPS válida de Conecta/TransCayma se normaliza a LecturaGPS."""
    trama = {
        "lat": -16.3900,
        "lon": -71.5400,
        "velocidad": 32.5,
        "antiguedad_seg": 3,
        "en_corredor": True,
    }
    lectura = normalizar_trama_gps(trama)
    assert isinstance(lectura, LecturaGPS)
    assert lectura.latitud == pytest.approx(-16.3900)
    assert lectura.longitud == pytest.approx(-71.5400)
    assert lectura.velocidad_kmh == pytest.approx(32.5)
    assert lectura.antiguedad_seg == 3
    assert lectura.en_corredor is True


@pytest.mark.parametrize(
    "trama_invalida",
    [
        None,
        {},
        {"lat": -16.39, "lon": None, "velocidad": 25.0},
        {"lat": -16.39, "velocidad": 25.0},
    ],
)
def test_issue_03_maneja_gps_sin_datos(trama_invalida):
    """ISSUE-03: ante una trama GPS sin datos o incompleta, debe lanzar DatosGPSIncompletosError."""
    with pytest.raises(DatosGPSIncompletosError):
        normalizar_trama_gps(trama_invalida)
