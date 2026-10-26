"""Patrón Strategy + Factory para algoritmos intercambiables de tiempo estimado de llegada (ETA)."""
from abc import ABC, abstractmethod


class EstrategiaETA(ABC):
    """STRATEGY: contrato común para calcular el ETA (en minutos) según las condiciones de tránsito."""

    @abstractmethod
    def calcular(self, distancia_km: float, velocidad_kmh: float) -> float:
        pass


class ETAFlujoLibre(EstrategiaETA):
    def calcular(self, distancia_km: float, velocidad_kmh: float) -> float:
        vel_efectiva = max(velocidad_kmh, 15.0)
        return (distancia_km / vel_efectiva) * 60.0


class ETAHoraPunta(EstrategiaETA):
    def calcular(self, distancia_km: float, velocidad_kmh: float) -> float:
        vel_efectiva = max(velocidad_kmh, 15.0)
        return (distancia_km / vel_efectiva) * 60.0 * 1.45


class ETAClimaLluvia(EstrategiaETA):
    def calcular(self, distancia_km: float, velocidad_kmh: float) -> float:
        vel_efectiva = max(velocidad_kmh, 15.0)
        return (distancia_km / vel_efectiva) * 60.0 * 1.30 + 3.0


class FabricaEstrategiasETA:
    """FACTORY (registro): permite agregar nuevos algoritmos de ETA cumpliendo Open/Closed."""

    def __init__(self):
        self._estrategias = {
            "FLUJO_LIBRE": ETAFlujoLibre,
            "HORA_PUNTA": ETAHoraPunta,
            "CLIMA_LLUVIA": ETAClimaLluvia,
        }

    def registrar(self, modo: str, creador):
        self._estrategias[modo] = creador

    def crear(self, modo: str) -> EstrategiaETA:
        if modo not in self._estrategias:
            raise ValueError(f"Algoritmo de ETA no soportado: {modo}")
        return self._estrategias[modo]()