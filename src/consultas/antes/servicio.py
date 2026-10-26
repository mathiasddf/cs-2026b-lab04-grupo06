"""Versión ingenua (antes del refactor) del flujo crítico: Consultar ETA y explicar retrasos."""
from dataclasses import dataclass, field
from typing import List, Optional
from src.consultas.externos import GpsConectaSDK, GpsTransCaymaClient, ClienteLLMFalso


@dataclass
class SegmentoRuta:
    nombre: str
    distancia_km: float


@dataclass
class Viaje:
    id: str
    placa: str
    operador: str
    estado: str = "PROGRAMADO"
    segmentos: List[SegmentoRuta] = field(default_factory=list)
    eta_minutos: float = 0.0
    alerta: Optional[str] = None


class ServicioConsultas:
    def __init__(self, gps_conecta=None, gps_cayma=None, llm=None):
        self.gps_conecta = gps_conecta or GpsConectaSDK()
        self.gps_cayma = gps_cayma or GpsTransCaymaClient()
        self.llm = llm or ClienteLLMFalso()
        self.eventos: List[str] = []

    def consultar_eta(self, viaje: Viaje, modo_calculo: str = "FLUJO_LIBRE", pasajero_id: str = "P01") -> dict:
        if viaje.estado == "FINALIZADO":
            raise ValueError("El viaje ya ha finalizado")
        if not viaje.segmentos:
            raise ValueError("El pedido/viaje no tiene segmentos pendientes")

        vel_kmh, age_sec, en_corredor = 0.0, 0, True
        if viaje.operador == "CONECTA":
            exito = False
            for intento in range(3):
                try:
                    r = self.gps_conecta.obtener_telemetria(viaje.placa)
                    vel_kmh = r["speed_kmh"]
                    age_sec = r["age_sec"]
                    en_corredor = r["en_corredor"]
                    exito = True
                    break
                except TimeoutError:
                    if intento == 2:
                        exito = False
            if not exito:
                age_sec = 999
        elif viaje.operador == "TRANSCAYMA":
            exito = False
            for intento in range(3):
                try:
                    codigo, data = self.gps_cayma.fetch_position(viaje.id)
                    if codigo == 200:
                        vel_kmh = data["vel_ms"] * 3.6
                        age_sec = data["seconds_ago"]
                        en_corredor = not data["off_route"]
                        exito = True
                    break
                except TimeoutError:
                    if intento == 2:
                        exito = False
            if not exito:
                age_sec = 999
        else:
            raise ValueError(f"Operador GPS no soportado: {viaje.operador}")

        if viaje.estado == "PROGRAMADO":
            if vel_kmh > 0 and age_sec <= 60:
                viaje.estado = "EN_RUTA"
            else:
                raise ValueError("El viaje programado aún no inicia recorrido")

        if age_sec > 60:
            viaje.estado = "DETENIDO"
            viaje.alerta = "Bus sin señal por más de 60s"
        elif not en_corredor:
            viaje.estado = "DESVIADO"
            viaje.alerta = "Bus desviado de su corredor permitido"
        else:
            viaje.estado = "EN_RUTA"
            viaje.alerta = None

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

    def explicar_retraso(self, viaje: Viaje, eventos_ruta: List[str], proveedor: str = "CLAUDE") -> str:
        prompt = f"Explica el retraso del bus {viaje.placa} ({viaje.estado}): {', '.join(eventos_ruta)}"
        if proveedor in ("CLAUDE", "LOCAL"):
            texto = self.llm.generar(prompt)
        else:
            raise ValueError(f"Proveedor LLM no soportado: {proveedor}")

        if " min" in texto.lower() or "minutos" in texto.lower():
            raise ValueError("Guardrail: la IA inventó un tiempo de llegada no verificado")
        for prohibida in ["garantizado", "sin tráfico", "100% seguro", "accidente fatal"]:
            if prohibida in texto.lower():
                raise ValueError(f"Guardrail: afirmación no permitida '{prohibida}'")
        if len(texto) > 180:
            raise ValueError("Guardrail: explicación demasiado larga para pantalla de paradero")
        return texto