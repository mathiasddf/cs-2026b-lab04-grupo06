"""Servicio principal de RutaSIT Arequipa después del refactor hacia patrones GoF."""
from dataclasses import dataclass
from typing import List
from src.consultas.externos import GpsConectaSDK, GpsTransCaymaClient, ClienteLLMFalso
from src.consultas.proveedores_gps import (
    FabricaProveedoresGPS,
    ConectaGpsAdapter,
    TransCaymaGpsAdapter,
)
from src.consultas.estrategias_eta import FabricaEstrategiasETA
from src.consultas.estados import MAPA_ESTADOS_INICIALES, EstadoViaje
from src.consultas.eventos import (
    PublicadorEventos,
    NotificadorPushPasajero,
    MonitorPanelOperador,
    PantallaParadero,
)
from src.consultas.ia import (
    ClaudeAdapter,
    LocalLLMAdapter,
    ConCacheLLM,
    ExplicadorRetrasosIA,
)


@dataclass
class SegmentoRuta:
    nombre: str
    distancia_km: float


class Viaje:
    def __init__(
        self,
        id: str,
        placa: str,
        operador: str,
        estado: str = "PROGRAMADO",
        segmentos: List[SegmentoRuta] | None = None,
    ):
        self.id = id
        self.placa = placa
        self.operador = operador
        self.segmentos = segmentos if segmentos is not None else []
        self.eta_minutos: float = 0.0
        self.alerta: str | None = None
        self._estado: EstadoViaje = MAPA_ESTADOS_INICIALES[estado]()

    @property
    def estado(self) -> str:
        return self._estado.nombre

    @property
    def es_anomalo(self) -> bool:
        return self._estado.es_anomalo

    def cambiar_a(self, nuevo_estado: EstadoViaje):
        self._estado = nuevo_estado

    def actualizar_ubicacion(self, lectura):
        if not self.segmentos:
            raise ValueError("El viaje no tiene segmentos pendientes")
        self._estado.procesar_ubicacion(self, lectura)

    def finalizar(self):
        self._estado.finalizar(self)

    def distancia_pendiente(self) -> float:
        return sum(s.distancia_km for s in self.segmentos)


class ServicioConsultas:
    def __init__(
        self,
        gps_conecta=None,
        gps_cayma=None,
        llm=None,
        fabrica_gps=None,
        fabrica_eta=None,
        publicador=None,
    ):
        self.gps_conecta = gps_conecta or GpsConectaSDK()
        self.gps_cayma = gps_cayma or GpsTransCaymaClient()
        self.llm = llm or ClienteLLMFalso()
        self.eventos: List[str] = []

        self.fabrica_gps = fabrica_gps or self._crear_fabrica_gps_default()
        self.fabrica_eta = fabrica_eta or FabricaEstrategiasETA()
        self.publicador = publicador or self._crear_publicador_default()

        adaptador_llm = ConCacheLLM(ClaudeAdapter(self.llm))
        self.explicador = ExplicadorRetrasosIA(
            {
                "CLAUDE": adaptador_llm,
                "LOCAL": ConCacheLLM(LocalLLMAdapter(self.llm)),
            }
        )

    def _crear_fabrica_gps_default(self) -> FabricaProveedoresGPS:
        f = FabricaProveedoresGPS()
        f.registrar("CONECTA", lambda: ConectaGpsAdapter(self.gps_conecta))
        f.registrar("TRANSCAYMA", lambda: TransCaymaGpsAdapter(self.gps_cayma))
        return f

    def _crear_publicador_default(self) -> PublicadorEventos:
        pub = PublicadorEventos()
        pub.suscribir("viaje_anomalo", NotificadorPushPasajero(self.eventos))
        pub.suscribir("viaje_anomalo", MonitorPanelOperador(self.eventos))
        pub.suscribir("viaje_en_ruta", PantallaParadero(self.eventos))
        return pub

    def consultar_eta(
        self, viaje: Viaje, modo_calculo: str = "FLUJO_LIBRE", pasajero_id: str = "P01"
    ) -> dict:
        proveedor_gps = self.fabrica_gps.crear(viaje.operador)
        estrategia_eta = self.fabrica_eta.crear(modo_calculo)
        identificador = viaje.placa if viaje.operador == "CONECTA" else viaje.id
        lectura = proveedor_gps.obtener_lectura(identificador)

        viaje.actualizar_ubicacion(lectura)
        eta_base = estrategia_eta.calcular(viaje.distancia_pendiente(), lectura.velocidad_kmh)
        penalidad = 8.0 if viaje.es_anomalo else 0.0
        viaje.eta_minutos = round(eta_base + penalidad, 2)

        evento = "viaje_anomalo" if viaje.es_anomalo else "viaje_en_ruta"
        self.publicador.publicar(
            evento,
            {
                "id": viaje.id,
                "pasajero_id": pasajero_id,
                "estado": viaje.estado,
                "eta": viaje.eta_minutos,
                "alerta": viaje.alerta,
            },
        )
        return {"estado": viaje.estado, "eta_min": viaje.eta_minutos, "alerta": viaje.alerta}

    def explicar_retraso(
        self, viaje: Viaje, eventos_ruta: List[str], proveedor: str = "CLAUDE"
    ) -> str:
        return self.explicador.explicar(viaje.placa, viaje.estado, eventos_ruta, proveedor)