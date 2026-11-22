"""Pruebas del ISSUE-02: Desvío no detectado en curvas del corredor."""
from src.consultas.estados import esta_en_corredor_curva

# Polilínea en L: tramo Av. Ejército -> giro hacia Av. Cayma
CURVA_EJERCITO_CAYMA = [
    (-16.3900, -71.5450),
    (-16.3900, -71.5350),
    (-16.3800, -71.5350),
]


def test_issue_02_caso_normal_bus_sobre_la_curva():
    """Caso feliz: un bus circulando sobre el tramo de Av. Cayma dentro de la tolerancia está en corredor."""
    posicion_en_corredor = (-16.3850, -71.5355)
    assert esta_en_corredor_curva(posicion_en_corredor, CURVA_EJERCITO_CAYMA, tolerancia=0.002) is True


def test_issue_02_detecta_desvio_en_curva():
    """ISSUE-02: un bus dentro del bounding box pero alejado de los segmentos de la curva debe marcar desvío (False)."""
    posicion_desviada = (-16.3820, -71.5430)
    assert esta_en_corredor_curva(posicion_desviada, CURVA_EJERCITO_CAYMA, tolerancia=0.002) is False, (
        "El bus se desvió ~880 m fuera de la curva Av. Ejército -> Cayma, pero no fue detectado."
    )
