"""Tácticas de disponibilidad (Iteración 2 de ADD - QA-02): Circuit Breaker + Fallback a Última Posición Conocida (Last-Known Location en PostgreSQL) implementados como Decorator sobre el puerto ProveedorGPS del Laboratorio 07. """
from __future__ import annotations
import time
from typing import Callable
from src.consultas.proveedores_gps import LecturaGPS, ProveedorGPS

class CircuitoAbiertoGPS(Exception):
    """Falla rápida cuando el SDK GPS de una concesionaria acumula fallas consecutivas."""
    pass

class RepositorioUltimaPosicion:
    """Simula la tabla persistente 'ultima_posicion_bus' en PostgreSQL/PostGIS (Last-Known Location). A diferencia de guardar solo en Redis volátil, persiste en disco y sobrevive reinicios."""

    def __init__(self):
        self._tabla: dict[str, tuple[LecturaGPS, float]] = {}

    def guardar(self, identificador: str, lectura: LecturaGPS, instante: float) -> None:
        self._tabla[identificador] = (lectura, instante)

    def obtener_degradada(self, identificador: str, instante_actual: float) -> LecturaGPS:
        if identificador not in self._tabla:
            # Si nunca reportó antes, retorna lectura sin señal (antigüedad 999s -> estado DETENIDO)
            return LecturaGPS(0.0, 0.0, 0.0, 999, True)
        lectura_previa, t_guardado = self._tabla[identificador]
        delta_s = max(0, int(instante_actual - t_guardado))
        # Conserva la velocidad e historial del corredor pero actualiza la antigüedad real
        return LecturaGPS(
            latitud=lectura_previa.latitud,
            longitud=lectura_previa.longitud,
            velocidad_kmh=lectura_previa.velocidad_kmh,
            antiguedad_seg=lectura_previa.antiguedad_seg + delta_s,
            en_corredor=lectura_previa.en_corredor,
        )

class ConCircuitBreakerGPS(ProveedorGPS):
    """DECORATOR que combina las tácticas 'Detectar fallas', 'Prevenir fallas' (Circuit Breaker) y 'Degradación elegante' (Fallback a última posición válida en PostgreSQL)."""

    def __init__(
        self,
        interno: ProveedorGPS,
        repositorio: RepositorioUltimaPosicion | None = None,
        umbral_fallas: int = 3,
        espera_s: float = 60.0,
        reloj: Callable[[], float] = time.monotonic,
    ):
        self._interno = interno
        self._repo = repositorio or RepositorioUltimaPosicion()
        self._umbral = umbral_fallas
        self._espera_s = espera_s
        self._reloj = reloj
        self._fallas = 0
        self._abierto_desde: float | None = None
        self.lecturas_degradadas = 0

    @property
    def estado(self) -> str:
        if self._abierto_desde is None:
            return "CERRADO"
        if self._reloj() - self._abierto_desde >= self._espera_s:
            return "SEMIABIERTO"
        return "ABIERTO"

    def obtener_lectura(self, identificador: str) -> LecturaGPS:
        ahora = self._reloj()
        if self.estado == "ABIERTO":
            self.lecturas_degradadas += 1
            return self._repo.obtener_degradada(identificador, ahora)

        try:
            lectura = self._interno.obtener_lectura(identificador)
        except TimeoutError:
            self._registrar_falla(ahora)
            self.lecturas_degradadas += 1
            return self._repo.obtener_degradada(identificador, ahora)

        # Éxito: si la lectura es válida (< 999s), cierra el circuito y actualiza Last-Known en BD
        if lectura.antiguedad_seg < 999:
            self._fallas = 0
            self._abierto_desde = None
            self._repo.guardar(identificador, lectura, ahora)
        return lectura

    def _registrar_falla(self, ahora: float) -> None:
        self._fallas += 1
        if self._fallas >= self._umbral or self.estado == "SEMIABIERTO":
            self._abierto_desde = ahora