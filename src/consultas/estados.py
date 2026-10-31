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