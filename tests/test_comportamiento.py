import pytest
import importlib
from src.consultas.antes.servicio import ServicioConsultas, Viaje, SegmentoRuta

@pytest.fixture(params=["src.consultas.antes.servicio"])
def servicio(request):
    mod = importlib.import_module(request.param)
    return mod.ServicioConsultas()

@pytest.fixture
def viaje_valido():
    return Viaje(
        id="V-101",
        placa="ABC-123",
        operador="CONECTA",
        estado="PROGRAMADO",
        segmentos=[SegmentoRuta("Seg-1", 5.0), SegmentoRuta("Seg-2", 3.0)]
    )

# 1. Éxito Operador CONECTA
def test_consultar_eta_conecta_exito(servicio, viaje_valido):
    res = servicio.consultar_eta(viaje_valido, modo_calculo="FLUJO_LIBRE")
    assert res["estado"] == "EN_RUTA"
    assert res["eta_min"] > 0
    assert res["alerta"] is None

# 2. Éxito Operador TRANSCAYMA
def test_consultar_eta_transcayma_exito(servicio, viaje_valido):
    viaje_valido.operador = "TRANSCAYMA"
    res = servicio.consultar_eta(viaje_valido, modo_calculo="FLUJO_LIBRE")
    assert res["estado"] == "EN_RUTA"

# 3. Error: Viaje finalizado
def test_error_viaje_finalizado(servicio, viaje_valido):
    viaje_valido.estado = "FINALIZADO"
    with pytest.raises(ValueError, match="El viaje ya ha finalizado"):
        servicio.consultar_eta(viaje_valido)

# 4. Error: Sin segmentos
def test_error_sin_segmentos(servicio, viaje_valido):
    viaje_valido.segmentos = []
    with pytest.raises(ValueError, match="no tiene segmentos pendientes"):
        servicio.consultar_eta(viaje_valido)

# 5. Error: Operador no soportado
def test_error_operador_desconocido(servicio, viaje_valido):
    viaje_valido.operador = "GPS_DESCONOCIDO"
    with pytest.raises(ValueError, match="Operador GPS no soportado"):
        servicio.consultar_eta(viaje_valido)

# 6. Error: Algoritmo/Modo no soportado
def test_error_modo_calculo_invalido(servicio, viaje_valido):
    with pytest.raises(ValueError, match="Algoritmo de ETA no soportado"):
        servicio.consultar_eta(viaje_valido, modo_calculo="MODO_INVALIDO")

# 7. Explicar retraso con IA (Éxito)
def test_explicar_retraso_exito(servicio, viaje_valido):
    explicacion = servicio.explicar_retraso(viaje_valido, ["Detenido en semáforo"], proveedor="CLAUDE")
    assert isinstance(explicacion, str)
    assert len(explicacion) <= 180

# 8. Guardrail IA: Texto demasiado largo
def test_explicar_retraso_guardrail_longitud(servicio, viaje_valido):
    servicio.llm.generar = lambda p: "A" * 200
    with pytest.raises(ValueError, match="Guardrail: explicación demasiado larga"):
        servicio.explicar_retraso(viaje_valido, ["Trafico intenso"])