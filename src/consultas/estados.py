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
        viaje.estado_obj = EstadoEnRuta()


class EstadoEnRuta(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "EN_RUTA"

    def desviar(self, viaje, motivo: str) -> None:
        viaje.estado_obj = EstadoDesviado()
        viaje.alerta = motivo

    def detener(self, viaje, motivo: str) -> None:
        viaje.estado_obj = EstadoDetenido()
        viaje.alerta = motivo

    def finalizar(self, viaje) -> None:
        viaje.estado_obj = EstadoFinalizado()


class EstadoDesviado(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "DESVIADO"

    def reanudar(self, viaje) -> None:
        viaje.estado_obj = EstadoEnRuta()
        viaje.alerta = None

    def finalizar(self, viaje) -> None:
        viaje.estado_obj = EstadoFinalizado()


class EstadoDetenido(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "DETENIDO"

    def reanudar(self, viaje) -> None:
        viaje.estado_obj = EstadoEnRuta()
        viaje.alerta = None

    def finalizar(self, viaje) -> None:
        viaje.estado_obj = EstadoFinalizado()


class EstadoFinalizado(EstadoViajeBase):
    @property
    def nombre(self) -> str:
        return "FINALIZADO"