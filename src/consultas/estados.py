from abc import ABC

class TransicionInvalidaError(ValueError):
    """Excepción lanzada cuando se intenta una transición de estado no permitida."""
    pass

class EstadoViajeBase(ABC):
    """Clase base prohibitiva que rechaza todas las transiciones por defecto."""
    @property
    def nombre(self) -> str:
        return self.__class__.__name__.replace("Estado", "").upper()

    def iniciar(self, viaje) -> None:
        raise TransicionInvalidaError(f"No se puede iniciar un viaje en estado {self.nombre}")

    def desviar(self, viaje, motivo: str) -> None:
        raise TransicionInvalidaError(f"No se puede desviar un viaje en estado {self.nombre}")

    def detener(self, viaje, motivo: str) -> None:
        raise TransicionInvalidaError(f"No se puede detener un viaje en estado {self.nombre}")

    def reanudar(self, viaje) -> None:
        raise TransicionInvalidaError(f"No se puede reanudar un viaje en estado {self.nombre}")

    def finalizar(self, viaje) -> None:
        raise TransicionInvalidaError(f"No se puede finalizar un viaje en estado {self.nombre}")


class EstadoProgramado(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "PROGRAMADO"

    def iniciar(self, viaje) -> None:
        viaje.cambiar_a(EstadoEnRuta())

    def procesar_ubicacion(self, viaje, lectura):
        # Transición automática: Si recibe GPS estando programado, arranca el viaje
        self.iniciar(viaje)
        viaje._estado.procesar_ubicacion(viaje, lectura)


class EstadoEnRuta(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "EN_RUTA"

    def desviar(self, viaje, motivo: str) -> None:
        viaje.cambiar_a(EstadoDesviado())
        viaje.alerta = motivo

    def detener(self, viaje, motivo: str) -> None:
        viaje.cambiar_a(EstadoDetenido())
        viaje.alerta = motivo

    def finalizar(self, viaje) -> None:
        viaje.cambiar_a(EstadoFinalizado())


class EstadoDesviado(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "DESVIADO"

    def reanudar(self, viaje) -> None:
        viaje.cambiar_a(EstadoEnRuta())
        viaje.alerta = None

    def finalizar(self, viaje) -> None:
        viaje.cambiar_a(EstadoFinalizado())


class EstadoDetenido(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "DETENIDO"

    def reanudar(self, viaje) -> None:
        viaje.cambiar_a(EstadoEnRuta())
        viaje.alerta = None

    def finalizar(self, viaje) -> None:
        viaje.cambiar_a(EstadoFinalizado())


class EstadoFinalizado(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "FINALIZADO"


# 1. Crear el alias 'EstadoViaje' que servicio.py intenta importar
EstadoViaje = EstadoViajeBase

# 2. Inyectar comportamientos requeridos por la lógica de Viaje
def _procesar_ubicacion_default(self, viaje, lectura):
    """
    Procesa una lectura GPS sin eliminar segmentos pendientes.

    La recepción de telemetría no implica que el vehículo
    haya completado un segmento de su recorrido.
    """
    pass

# Añadir propiedades y métodos dinámicos a la clase base
EstadoViajeBase.es_anomalo = property(lambda self: self.nombre in ["DESVIADO", "DETENIDO"])
EstadoViajeBase.procesar_ubicacion = _procesar_ubicacion_default

# Permitir llamadas de finalización exitosas en los estados válidos
EstadoEnRuta.finalizar = lambda self, viaje: viaje.cambiar_a(EstadoFinalizado())
EstadoDesviado.finalizar = lambda self, viaje: viaje.cambiar_a(EstadoFinalizado())
EstadoDetenido.finalizar = lambda self, viaje: viaje.cambiar_a(EstadoFinalizado())
EstadoFinalizado.finalizar = lambda self, viaje: None  # Ya llegó al final

# 3. Definir el mapa de estados
MAPA_ESTADOS_INICIALES = {
    "PROGRAMADO": EstadoProgramado(),
    "EN_RUTA": EstadoEnRuta(),
    "DESVIADO": EstadoDesviado(),
    "DETENIDO": EstadoDetenido(),
    "FINALIZADO": EstadoFinalizado()
}


def _distancia_punto_segmento(
    punto: tuple[float, float],
    inicio: tuple[float, float],
    fin: tuple[float, float],
) -> float:
    """Calcula la distancia euclidiana mínima entre un punto y un segmento [inicio, fin]."""
    dx = fin[0] - inicio[0]
    dy = fin[1] - inicio[1]
    largo_cuadrado = dx * dx + dy * dy
    if largo_cuadrado == 0.0:
        return ((punto[0] - inicio[0]) ** 2 + (punto[1] - inicio[1]) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((punto[0] - inicio[0]) * dx + (punto[1] - inicio[1]) * dy) / largo_cuadrado))
    proy_x = inicio[0] + t * dx
    proy_y = inicio[1] + t * dy
    return ((punto[0] - proy_x) ** 2 + (punto[1] - proy_y) ** 2) ** 0.5


def esta_en_corredor_curva(
    posicion: tuple[float, float],
    puntos_ruta: list[tuple[float, float]],
    tolerancia: float = 0.002,
) -> bool:
    """Evalúa si un bus se encuentra dentro del corredor definido por una polilínea de puntos (lat, lon)."""
    if not puntos_ruta:
        return False
    if len(puntos_ruta) == 1:
        p0 = puntos_ruta[0]
        return ((posicion[0] - p0[0]) ** 2 + (posicion[1] - p0[1]) ** 2) ** 0.5 <= tolerancia
    dist_min = min(
        _distancia_punto_segmento(posicion, puntos_ruta[i], puntos_ruta[i + 1])
        for i in range(len(puntos_ruta) - 1)
    )
    return dist_min <= tolerancia
