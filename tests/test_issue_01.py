"""Pruebas del ISSUE-01: Tiempo de llegada (ETA) negativo si el bus ya pasó el paradero."""
import pytest
from src.consultas.estrategias_eta import ETAFlujoLibre, calcular_eta_a_paradero


def test_issue_01_caso_normal_bus_antes_del_paradero():
    """Caso feliz: el bus está antes del paradero y el ETA en minutos es positivo."""
    eta = calcular_eta_a_paradero(
        posicion_bus_km=4.0,
        posicion_paradero_km=6.0,
        velocidad_kmh=30.0,
        estrategia=ETAFlujoLibre(),
    )
    assert eta == pytest.approx(4.0)


def test_issue_01_eta_no_negativo_si_bus_paso_paradero():
    """ISSUE-01: si el bus ya pasó el paradero, el ETA nunca debe ser negativo (debe retornar 0.0)."""
    eta = calcular_eta_a_paradero(
        posicion_bus_km=8.0,
        posicion_paradero_km=6.0,
        velocidad_kmh=30.0,
        estrategia=ETAFlujoLibre(),
    )
    assert eta == 0.0, f"Se esperaba 0.0 min cuando el bus ya pasó el paradero, pero se obtuvo {eta}"
