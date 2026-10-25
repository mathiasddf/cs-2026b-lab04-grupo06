"""Patrón Observer: desacopla la emisión de eventos de ETA y anomalías de sus suscriptores."""
from abc import ABC, abstractmethod


class SuscriptorRuta(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict):
        pass


class PublicadorEventos:
    def __init__(self):
        self._suscriptores: dict[str, list[SuscriptorRuta]] = {}

    def suscribir(self, evento: str, suscriptor: SuscriptorRuta):
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict):
        for s in self._suscriptores.get(evento, []):
            s.actualizar(evento, datos)


class NotificadorPushPasajero(SuscriptorRuta):
    def __init__(self, bandeja: list):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict):
        self._bandeja.append(
            f"push:{datos['pasajero_id']}:{datos['alerta']} (ETA: {datos['eta']:.2f} min)"
        )


class MonitorPanelOperador(SuscriptorRuta):
    def __init__(self, bandeja: list):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict):
        self._bandeja.append(
            f"panel:{datos['id']}:{datos['estado']}:{datos['eta']:.2f}"
        )


class PantallaParadero(SuscriptorRuta):
    def __init__(self, bandeja: list):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict):
        self._bandeja.append(
            f"paradero:{datos['id']}:ETA {datos['eta']:.2f} min"
        )