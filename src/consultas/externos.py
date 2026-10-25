"""Servicios externos simulados para RutaSIT Arequipa (GPS de operadores y proveedores LLM)."""

class GpsConectaSDK:
    """SDK del Operador A (ConectaAQP): devuelve diccionario con lat/lon, speed_kmh y age_sec."""
    def __init__(self, fallas: int = 0, lat: float = -16.4090, lon: float = -71.5375,
                 speed_kmh: float = 30.0, age_sec: int = 5, en_corredor: bool = True):
        self.fallas = fallas
        self.llamadas = 0
        self._lat = lat
        self._lon = lon
        self._speed_kmh = speed_kmh
        self._age_sec = age_sec
        self._en_corredor = en_corredor

    def obtener_telemetria(self, placa: str) -> dict:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("Timeout al consultar GPS ConectaAQP")
        return {
            "ok": True,
            "lat": self._lat,
            "lon": self._lon,
            "speed_kmh": self._speed_kmh,
            "age_sec": self._age_sec,
            "en_corredor": self._en_corredor,
        }


class GpsTransCaymaClient:
    """Cliente del Operador B (TransCayma): devuelve tupla (codigo_http, payload) con velocidad en m/s."""
    def __init__(self, fallas: int = 0, lat: float = -16.4090, lon: float = -71.5375,
                 speed_ms: float = 8.3333, age_sec: int = 5, desviado: bool = False):
        self.fallas = fallas
        self.llamadas = 0
        self._lat = lat
        self._lon = lon
        self._speed_ms = speed_ms
        self._age_sec = age_sec
        self._desviado = desviado

    def fetch_position(self, bus_id: str) -> tuple:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("Timeout en GpsTransCaymaClient")
        return (200, {
            "coords": (self._lat, self._lon),
            "vel_ms": self._speed_ms,
            "seconds_ago": self._age_sec,
            "off_route": self._desviado,
        })


class ClienteLLMFalso:
    """Doble de prueba para simular respuestas de Claude / Gemini / LLM Local sin red ni API key."""
    def __init__(self, respuesta: str = "Retraso moderado en Av. Ejército por congestión vehicular en hora punta."):
        self.respuesta = respuesta
        self.llamadas = 0

    def generar(self, prompt: str) -> str:
        self.llamadas += 1
        return self.respuesta