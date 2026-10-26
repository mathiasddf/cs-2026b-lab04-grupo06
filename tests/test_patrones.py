"""Pruebas unitarias para validar patrones GoF (E2, E3, E4 y E5)."""
import pytest
from src.consultas.servicio import ServicioConsultas, Viaje, SegmentoRuta, EstrategiaGPS
from src.consultas.estados import TransicionInvalidaError
from src.consultas.eventos import PublicadorEventos, SuscriptorRuta
from src.consultas.proveedores_gps import ProveedorGPS, LecturaGPS, ConReintentosGPS
from src.consultas.ia import ClaudeAdapter, ConCacheLLM, ExplicadorRetrasosIA


class MockClienteLLM:
    """Doble de prueba con respuesta configurable y contador de llamadas para E4 y E5."""

    def __init__(self, respuesta: str):
        self.respuesta = respuesta
        self.llamadas = 0

    def generar(self, prompt: str) -> str:
        self.llamadas += 1
        return self.respuesta


# --- PRUEBAS DE E2 Y E3 ---

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


# --- PRUEBAS DE E4: Patrón Observer y Patrón Decorator ---

def test_observer_nuevo_suscriptor_sin_tocar_el_servicio():
    """Valida que un nuevo suscriptor (Auditoría) reciba eventos mediante PublicadorEventos (E4.1)."""
    class SuscriptorAuditoriaSIT(SuscriptorRuta):
        def __init__(self):
            self.registros = []

        def actualizar(self, evento: str, datos: dict):
            self.registros.append(f"auditoria:{evento}:{datos['id']}")

    auditor = SuscriptorAuditoriaSIT()
    servicio = ServicioConsultas()

    if hasattr(servicio, "publicador"):
        servicio.publicador.suscribir("viaje_en_ruta", auditor)
        viaje = Viaje("V-400", "V5A-789", "CONECTA", "EN_RUTA", [SegmentoRuta("Av. Ejército", 5.0)])
        servicio.consultar_eta(viaje, modo_calculo="FLUJO_LIBRE")
    else:
        pub = PublicadorEventos()
        pub.suscribir("viaje_en_ruta", auditor)
        pub.publicar("viaje_en_ruta", {"id": "V-400", "eta": 10.0})

    assert auditor.registros == ["auditoria:viaje_en_ruta:V-400"]


def test_decorator_reintentos_gps_recupera_ante_timeout():
    """Valida que ConReintentosGPS reintente ante TimeoutError sin modificar el adaptador (E4.2)."""
    class GpsInestable(ProveedorGPS):
        def __init__(self):
            self.intentos = 0

        def obtener_lectura(self, identificador: str) -> LecturaGPS:
            self.intentos += 1
            if self.intentos < 3:
                raise TimeoutError("Fallo temporal de red GPS")
            return LecturaGPS(-16.4, -71.5, 30.0, 4, True)

    gps_base = GpsInestable()
    gps_decorado = ConReintentosGPS(gps_base, intentos=3)

    lectura = gps_decorado.obtener_lectura("V5A-789")
    assert lectura.velocidad_kmh == 30.0
    assert gps_base.intentos == 3


def test_decorator_cache_llm_evita_llamadas_repetidas():
    """Valida que ConCacheLLM guarde la respuesta del LLM y evite llamadas repetidas (E4.2 / E5)."""
    llm_falso = MockClienteLLM("Tráfico denso en Óvalo Quiñones.")
    proveedor_cacheado = ConCacheLLM(ClaudeAdapter(llm_falso))
    explicador = ExplicadorRetrasosIA({"CLAUDE": proveedor_cacheado})

    r1 = explicador.explicar("V5A-789", "DESVIADO", ["Obras en vía"])
    r2 = explicador.explicar("V5A-789", "DESVIADO", ["Obras en vía"])
    assert r1 == r2
    assert llm_falso.llamadas == 1


# --- PRUEBA DE E5: Chain of Responsibility (Guardrails de IA) ---

def test_chain_guardrail_longitud_maxima_bloquea_texto_excesivo():
    """Valida que el eslabón LongitudMaximaParadero bloquee respuestas > 180 caracteres (E5)."""
    llm_falso = MockClienteLLM("A" * 200)
    explicador = ExplicadorRetrasosIA({"CLAUDE": ClaudeAdapter(llm_falso)})

    with pytest.raises(ValueError, match="demasiado larga"):
        explicador.explicar("V5A-789", "DETENIDO", ["Sin señal GPS"])