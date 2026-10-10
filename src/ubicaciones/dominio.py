from enum import Enum
from typing import List, Optional
from abc import ABC, abstractmethod

class EstadoBus(Enum):
    PROGRAMADO = "PROGRAMADO"
    EN_RUTA = "EN_RUTA"
    DESVIADO = "DESVIADO"
    DETENIDO = "DETENIDO"
    FINALIZADO = "FINALIZADO"

class PosicionGPS:
    def __init__(self, latitud: float, longitud: float, velocidad: float, fecha_hora: str):
        self.latitud: float = latitud
        self.longitud: float = longitud
        self.velocidad: float = velocidad
        self.fecha_hora: str = fecha_hora

class Paradero:
    def __init__(self, id_paradero: str, nombre: str, latitud: float, longitud: float):
        self.id_paradero: str = id_paradero
        self.nombre: str = nombre
        self.latitud: float = latitud
        self.longitud: float = longitud

class Ruta:
    def __init__(self, id_ruta: str, nombre: str, codigo: str):
        self.id_ruta: str = id_ruta
        self.nombre: str = nombre
        self.codigo: str = codigo
        self.paraderos: List[Paradero] = []

class Bus:
    def __init__(self, id_bus: str, placa: str, capacidad: int):
        self.id_bus: str = id_bus
        self.placa: str = placa
        self.capacidad: int = capacidad
        self.estado: EstadoBus = EstadoBus.PROGRAMADO
        self.ruta_actual: Optional[Ruta] = None

class Viaje:
    def __init__(self, id_viaje: str, bus: Bus, ruta: Ruta):
        self.id_viaje: str = id_viaje
        self.bus: Bus = bus
        self.ruta: Ruta = ruta
        self.posiciones: List[PosicionGPS] = []
        self.eta_estimado_min: float = 0.0

class IServicioMapas(ABC):
    @abstractmethod
    def obtener_distancia(self, origen: PosicionGPS, destino: Paradero) -> float:
        pass