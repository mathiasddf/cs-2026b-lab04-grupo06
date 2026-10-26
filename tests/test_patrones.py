"""Pruebas unitarias que demuestran cada patrón GoF aplicado (E2 a E5)."""
import pytest
from src.consultas.servicio import ServicioConsultas, Viaje, SegmentoRuta
from src.consultas.proveedores_gps import LecturaGPS, ProveedorGPS
from src.consultas.estrategias_eta import EstrategiaETA
from src.consultas.eventos import SuscriptorRuta
from src.consultas.externos import ClienteLLMFalso


# --- Clases nuevas de prueba para demostrar Open/Closed (E2 y E4) ---

class GpsNuevoOperadorCharacato(ProveedorGPS):
    """Nuevo operador GPS agregado en el test sin tocar ServicioConsultas."""
    def obtener_lectura(self, identificador: str) -> LecturaGPS:
        return LecturaGPS(-16.45, -71.50, velocidad_kmh=25.0, antiguedad_seg=4, en_corredor=True)


class ETADiaFestivoArequipa(EstrategiaETA):
    """Nueva estrategia de ETA agregada en el test sin tocar ServicioConsultas."""
    def calcular(self, distancia_km: float, velocidad_kmh: float) -> float:
        return (distancia_km / max(velocidad_kmh, 15.0)) * 60.0 * 1.60


class SuscriptorAuditoriaSIT(SuscriptorRuta):
    """Nuevo suscriptor Observer agregado en el test sin tocar ServicioConsultas."""
    def __init__(self):
        self.registros = []

    def actualizar(self, evento: str, datos: dict):
        self.registros.append(f"auditoria:{evento}:{datos['id']}")


# --- PRUEBA DE E2: Strategy + Adapter + Factory (Open/Closed) ---

def test_open_closed_nuevo_operador_y_estrategia_eta_sin_modificar_servicio():
    s = ServicioConsultas()
    s.fabrica_gps.registrar("CHARACATO", GpsNuevoOperadorCharacato)
    s.fabrica_eta.registrar("FESTIVO_AQP", ETADiaFestivoArequipa)

    v = Viaje(
        id="V-200",
        placa="V9Z-111",
        operador="CHARACATO",
        estado="EN_RUTA",
        segmentos=[SegmentoRuta("Av. Dolores", 5.0)],
    )
    res = s.consultar_eta(v, modo_calculo="FESTIVO_AQP")
    assert res["estado"] == "EN_RUTA"
    assert res["eta_min"] == 19.2


# --- PRUEBA DE E3: Patrón State (Transiciones inválidas bloqueadas) ---

def test_state_impide_finalizar_viaje_programado_o_actualizar_finalizado():
    v_prog = Viaje(
        id="V-301",
        placa="V1A-001",
        operador="CONECTA",
        estado="PROGRAMADO",
        segmentos=[SegmentoRuta("Tramo 1", 2.0)],
    )
    with pytest.raises(ValueError, match="PROGRAMADO"):
        v_prog.finalizar()

    v_ruta = Viaje(
        id="V-302",
        placa="V1A-002",
        operador="CONECTA",
        estado="EN_RUTA",
        segmentos=[SegmentoRuta("Tramo 1", 2.0)],
    )
    v_ruta.finalizar()
    assert v_ruta.estado == "FINALIZADO"

    with pytest.raises(ValueError, match="finalizado"):
        v_ruta.actualizar_ubicacion(LecturaGPS(-16.4, -71.5, 30.0, 5, True))


# --- PRUEBA DE E4: Patrón Observer (Nuevo suscriptor sin tocar servicio) ---

def test_observer_nuevo_suscriptor_auditoria_sin_tocar_servicio():
    s = ServicioConsultas()
    auditor = SuscriptorAuditoriaSIT()
    s.publicador.suscribir("viaje_en_ruta", auditor)

    v = Viaje(
        id="V-400",
        placa="V5A-789",
        operador="CONECTA",
        estado="EN_RUTA",
        segmentos=[SegmentoRuta("Av. Ejército", 5.0)],
    )
    s.consultar_eta(v, modo_calculo="FLUJO_LIBRE")
    assert auditor.registros == ["auditoria:viaje_en_ruta:V-400"]


# --- PRUEBA DE E4/E5: Patrón Decorator (Caché de LLM evita llamadas repetidas) ---

def test_decorator_cache_llm_evita_llamadas_repetidas():
    llm_falso = ClienteLLMFalso("Tráfico denso en Óvalo Quiñones.")
    s = ServicioConsultas(llm=llm_falso)
    v = Viaje(id="V-500", placa="V5A-789", operador="CONECTA", estado="DESVIADO")

    r1 = s.explicar_retraso(v, ["Obras en vía"])
    r2 = s.explicar_retraso(v, ["Obras en vía"])
    assert r1 == r2
    assert llm_falso.llamadas == 1


# --- PRUEBA DE E5: Patrón Chain of Responsibility (Guardrail de longitud máxima) ---

def test_chain_guardrail_longitud_maxima_bloquea_texto_excesivo():
    texto_largo = "A" * 200
    llm_falso = ClienteLLMFalso(texto_largo)
    s = ServicioConsultas(llm=llm_falso)
    v = Viaje(id="V-600", placa="V5A-789", operador="CONECTA", estado="DETENIDO")

    with pytest.raises(ValueError, match="demasiado larga"):
        s.explicar_retraso(v, ["Sin señal GPS"])