"""Patrones Strategy + Adapter + Decorator + Factory para proveedores GPS de distintos operadores."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LecturaGPS:
    latitud: float
    longitud: float
    velocidad_kmh: float
    antiguedad_seg: int
    en_corredor: bool


class ProveedorGPS(ABC):
    """Puerto (interfaz común): desacopla el dominio de los SDK de cada operador de transporte."""

    @abstractmethod
    def obtener_lectura(self, identificador: str) -> LecturaGPS:
        pass


class ConectaGpsAdapter(ProveedorGPS):
    """ADAPTER: traduce el diccionario de GpsConectaSDK al objeto de dominio LecturaGPS."""

    def __init__(self, sdk):
        self._sdk = sdk

    def obtener_lectura(self, identificador: str) -> LecturaGPS:
        r = self._sdk.obtener_telemetria(identificador)
        return LecturaGPS(
            latitud=r["lat"],
            longitud=r["lon"],
            velocidad_kmh=float(r["speed_kmh"]),
            antiguedad_seg=int(r["age_sec"]),
            en_corredor=bool(r["en_corredor"]),
        )


class TransCaymaGpsAdapter(ProveedorGPS):
    """ADAPTER: traduce la tupla (HTTP, dict en m/s) de GpsTransCaymaClient a LecturaGPS (en km/h)."""

    def __init__(self, cliente):
        self._cliente = cliente

    def obtener_lectura(self, identificador: str) -> LecturaGPS:
        codigo, data = self._cliente.fetch_position(identificador)
        if codigo != 200:
            return LecturaGPS(0.0, 0.0, 0.0, 999, True)
        lat, lon = data["coords"]
        return LecturaGPS(
            latitud=lat,
            longitud=lon,
            velocidad_kmh=round(float(data["vel_ms"]) * 3.6, 4),
            antiguedad_seg=int(data["seconds_ago"]),
            en_corredor=not bool(data["off_route"]),
        )


class ConReintentosGPS(ProveedorGPS):
    """DECORATOR: agrega tolerancia a fallos (reintentos ante TimeoutError) sin tocar los adaptadores."""

    def __init__(self, interno: ProveedorGPS, intentos: int = 3):
        self._interno = interno
        self._intentos = intentos

    def obtener_lectura(self, identificador: str) -> LecturaGPS:
        for _ in range(self._intentos):
            try:
                return self._interno.obtener_lectura(identificador)
            except TimeoutError:
                continue
        return LecturaGPS(0.0, 0.0, 0.0, 999, True)


class FabricaProveedoresGPS:
    """FACTORY (registro): instancia el adaptador del operador y lo envuelve con ConReintentosGPS."""

    def __init__(self):
        self._creadores = {}

    def registrar(self, operador: str, creador):
        self._creadores[operador] = creador

    def crear(self, operador: str) -> ProveedorGPS:
        if operador not in self._creadores:
            raise ValueError(f"Operador GPS no soportado: {operador}")
        return ConReintentosGPS(self._creadores[operador]())


class DatosGPSIncompletosError(ValueError):
    """Excepción de dominio cuando una trama GPS llega vacía o con campos obligatorios faltantes."""
    pass


def _extraer_float_obligatorio(trama: dict, clave: str) -> float:
    valor = trama.get(clave)
    if valor is None or isinstance(valor, bool):
        raise DatosGPSIncompletosError(f"Campo GPS obligatorio faltante o nulo: '{clave}'")
    try:
        return float(valor)
    except (TypeError, ValueError) as exc:
        raise DatosGPSIncompletosError(f"Campo GPS '{clave}' no es numérico: {valor!r}") from exc


def _extraer_antiguedad(trama: dict) -> int:
    valor = trama.get("antiguedad_seg")
    if valor is None:
        return 0
    if isinstance(valor, bool):
        raise DatosGPSIncompletosError(f"Campo 'antiguedad_seg' inválido: {valor!r}")
    try:
        return int(valor)
    except (TypeError, ValueError) as exc:
        raise DatosGPSIncompletosError(f"Campo 'antiguedad_seg' inválido: {valor!r}") from exc


def normalizar_trama_gps(trama: dict | None) -> LecturaGPS:
    """Convierte una trama cruda de telemetría GPS (Conecta/TransCayma) en LecturaGPS."""
    if not isinstance(trama, dict) or not trama:
        raise DatosGPSIncompletosError("La trama GPS está vacía o no es un diccionario.")
    en_corredor_raw = trama.get("en_corredor")
    return LecturaGPS(
        latitud=_extraer_float_obligatorio(trama, "lat"),
        longitud=_extraer_float_obligatorio(trama, "lon"),
        velocidad_kmh=_extraer_float_obligatorio(trama, "velocidad"),
        antiguedad_seg=_extraer_antiguedad(trama),
        en_corredor=True if en_corredor_raw is None else bool(en_corredor_raw),
    )

