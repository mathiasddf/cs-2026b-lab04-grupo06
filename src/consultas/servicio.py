"""Servicio principal de RutaSIT Arequipa refactorizado con patrones GoF."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from abc import ABC, abstractmethod

from src.consultas.externos import GpsConectaSDK, GpsTransCaymaClient, ClienteLLMFalso
from src.consultas.estados import (
    EstadoViajeBase,
    EstadoProgramado,
    EstadoEnRuta,
    EstadoDesviado,
    EstadoDetenido,
    EstadoFinalizado,
    TransicionInvalidaError,
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
        segmentos: Optional[List[SegmentoRuta]] = None,
    ):
        self.id = id
        self.placa = placa
        self.operador = operador
        self.segmentos = segmentos or []
        self.eta_minutos: float = 0.0
        self.alerta: Optional[str] = None
        self.estado_obj: EstadoViajeBase = self._mapear_estado(estado)

    def _mapear_estado(self, estado_str: str) -> EstadoViajeBase:
        estados = {
            "PROGRAMADO": EstadoProgramado(),
            "EN_RUTA": EstadoEnRuta(),
            "DESVIADO": EstadoDesviado(),
            "DETENIDO": EstadoDetenido(),
            "FINALIZADO": EstadoFinalizado(),
        }
        return estados.get(estado_str, EstadoProgramado())

    @property
    def estado(self) -> str:
        return self.estado_obj.nombre

    def iniciar(self) -> None:
        self.estado_obj.iniciar(self)

    def desviar(self, motivo: str) -> None:
        self.estado_obj.desviar(self, motivo)

    def detener(self, motivo: str) -> None:
        self.estado_obj.detener(self, motivo)

    def reanudar(self) -> None:
        self.estado_obj.reanudar(self)

    def finalizar(self) -> None:
        self.estado_obj.finalizar(self)


class EstrategiaGPS(ABC):
    @abstractmethod
    def obtener_telemetria(self, viaje: Viaje) -> dict:
        pass


class AdaptadorGpsConecta(EstrategiaGPS):
    def __init__(self, sdk: Optional[GpsConectaSDK] = None):
        self.sdk = sdk or GpsConectaSDK()

    def obtener_telemetria(self, viaje: Viaje) -> dict:
        for intento in range(3):
            try:
                r = self.sdk.obtener_telemetria(viaje.placa)
                return {
                    "speed_kmh": r["speed_kmh"],
                    "age_sec": r["age_sec"],
                    "en_corredor": r["en_corredor"],
                }
            except TimeoutError:
                if intento == 2:
                    break
        return {"speed_kmh": 0.0, "age_sec": 999, "en_corredor": True}


class AdaptadorGpsTransCayma(EstrategiaGPS):
    def __init__(self, cliente: Optional[GpsTransCaymaClient] = None):
        self.cliente = cliente or GpsTransCaymaClient()

    def obtener_telemetria(self, viaje: Viaje) -> dict:
        for intento in range(3):
            try:
                codigo, data = self.cliente.fetch_position(viaje.id)
                if codigo == 200:
                    return {
                        "speed_kmh": data["vel_ms"] * 3.6,
                        "age_sec": data["seconds_ago"],
                        "en_corredor": not data["off_route"],
                    }
                break
            except TimeoutError:
                if intento == 2:
                    break
        return {"speed_kmh": 0.0, "age_sec": 999, "en_corredor": True}


class FabricaGPS:
    def __init__(self, gps_conecta=None, gps_cayma=None):
        self._estrategias: Dict[str, EstrategiaGPS] = {
            "CONECTA": AdaptadorGpsConecta(gps_conecta),
            "TRANSCAYMA": AdaptadorGpsTransCayma(gps_cayma),
        }

    def obtener_estrategia(self, operador: str) -> EstrategiaGPS:
        if operador not in self._estrategias:
            raise ValueError(f"Operador GPS no soportado: {operador}")
        return self._estrategias[operador]


class ServicioConsultas:
    def __init__(self, gps_conecta=None, gps_cayma=None, llm=None):
        self.fabrica_gps = FabricaGPS(gps_conecta, gps_cayma)
        self.llm = llm or ClienteLLMFalso()
        self.eventos: List[str] = []

    def consultar_eta(self, viaje: Viaje, modo_calculo: str = "FLUJO_LIBRE", pasajero_id: str = "P01") -> dict:
        if viaje.estado == "FINALIZADO":
            raise ValueError("El viaje ya ha finalizado")
        if not viaje.segmentos:
            raise ValueError("El pedido/viaje no tiene segmentos pendientes")

        estrategia = self.fabrica_gps.obtener_estrategia(viaje.operador)
        telemetria = estrategia.obtener_telemetria(viaje)
        vel_kmh, age_sec, en_corredor = telemetria["speed_kmh"], telemetria["age_sec"], telemetria["en_corredor"]

        if viaje.estado == "PROGRAMADO":
            if vel_kmh > 0 and age_sec <= 60:
                viaje.iniciar()
            else:
                raise ValueError("El viaje programado aún no inicia recorrido")

        if age_sec > 60:
            viaje.detener("Bus sin señal por más de 60s")
        elif not en_corredor:
            viaje.desviar("Bus desviado de su corredor permitido")

        distancia_total = sum(s.distancia_km for s in viaje.segmentos)
        vel_efectiva = max(vel_kmh, 15.0)
        
        if modo_calculo == "FLUJO_LIBRE":
            eta = (distancia_total / vel_efectiva) * 60.0
        elif modo_calculo == "HORA_PUNTA":
            eta = (distancia_total / vel_efectiva) * 60.0 * 1.45
        elif modo_calculo == "CLIMA_LLUVIA":
            eta = (distancia_total / vel_efectiva) * 60.0 * 1.30 + 3.0
        else:
            raise ValueError(f"Algoritmo de ETA no soportado: {modo_calculo}")

        if viaje.estado in ("DESVIADO", "DETENIDO"):
            eta = round(eta + 8.0, 2)
            self.eventos.append(f"push:{pasajero_id}:{viaje.alerta} (ETA: {eta:.2f} min)")
            self.eventos.append(f"panel:{viaje.id}:{viaje.estado}:{eta:.2f}")
        else:
            eta = round(eta, 2)
            self.eventos.append(f"paradero:{viaje.id}:ETA {eta:.2f} min")

        viaje.eta_minutos = eta
        return {"estado": viaje.estado, "eta_min": viaje.eta_minutos, "alerta": viaje.alerta}