"""Pruebas unitarias para validar patrones GoF (E2 y E3)."""
import pytest
from src.consultas.servicio import ServicioConsultas, Viaje, SegmentoRuta, EstrategiaGPS
from src.consultas.estados import TransicionInvalidaError


def test_open_closed_principle_agregar_nuevo_gps_sin_modificar_servicio():
    """Valida la inyección de un nuevo operador GPS sin alterar la clase ServicioConsultas."""
    class AdaptadorGpsSIT(EstrategiaGPS):
        def obtener_telemetria(self, viaje: Viaje) -> dict:
            return {"speed_kmh": 40.0, "age_sec": 5, "en_corredor": True}

    servicio = ServicioConsultas()
    servicio.fabrica_gps._estrategias["GPS_SIT"] = AdaptadorGpsSIT()

    viaje = Viaje("V-999", "XYZ-789", "GPS_SIT", "PROGRAMADO", [SegmentoRuta("S1", 10.0)])
    res = servicio.consultar_eta(viaje)
    assert res["estado"] == "EN_RUTA"
    assert res["eta_min"] > 0


def test_state_bloquea_transicion_invalida():
    """Valida que intentar finalizar un viaje PROGRAMADO sin haber iniciado lance TransicionInvalidaError."""
    viaje = Viaje(id="V-100", placa="ABC-123", operador="CONECTA", estado="PROGRAMADO")
    
    with pytest.raises(TransicionInvalidaError, match="No se puede finalizar un viaje en estado PROGRAMADO"):
        viaje.finalizar()


def test_state_transiciones_validas():
    """Valida el cambio de estado polimórfico a través de los métodos delegados."""
    viaje = Viaje(id="V-100", placa="ABC-123", operador="CONECTA", estado="PROGRAMADO")
    assert viaje.estado == "PROGRAMADO"
    
    viaje.iniciar()
    assert viaje.estado == "EN_RUTA"
    
    viaje.desviar("Tráfico intenso en Av. Ejército")
    assert viaje.estado == "DESVIADO"
    assert viaje.alerta == "Tráfico intenso en Av. Ejército"