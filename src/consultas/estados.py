"""Patrón State: implementa la máquina de estados del Viaje diseñada en el Laboratorio 05."""
from src.consultas.proveedores_gps import LecturaGPS


class EstadoViaje:
    """Clase base que prohíbe todas las transiciones por defecto."""
    nombre = "?"
    es_anomalo = False

    def procesar_ubicacion(self, viaje, lectura: LecturaGPS):
        raise ValueError(f"No se puede actualizar ubicación de un viaje en estado {self.nombre}")

    def finalizar(self, viaje):
        raise ValueError(f"No se puede finalizar un viaje en estado {self.nombre}")


def _transicionar_segun_lectura(viaje, lectura: LecturaGPS):
    if lectura.antiguedad_seg > 60:
        viaje.alerta = "Bus sin señal por más de 60s"
        viaje.cambiar_a(Detenido())
    elif not lectura.en_corredor:
        viaje.alerta = "Bus desviado de su corredor permitido"
        viaje.cambiar_a(Desviado())
    else:
        viaje.alerta = None
        viaje.cambiar_a(EnRuta())


class Programado(EstadoViaje):
    nombre = "PROGRAMADO"

    def procesar_ubicacion(self, viaje, lectura: LecturaGPS):
        if lectura.velocidad_kmh <= 0 or lectura.antiguedad_seg > 60:
            raise ValueError("El viaje programado aún no inicia recorrido")
        _transicionar_segun_lectura(viaje, lectura)


class EnRuta(EstadoViaje):
    nombre = "EN_RUTA"

    def procesar_ubicacion(self, viaje, lectura: LecturaGPS):
        _transicionar_segun_lectura(viaje, lectura)

    def finalizar(self, viaje):
        viaje.cambiar_a(Finalizado())


class Desviado(EstadoViaje):
    nombre = "DESVIADO"
    es_anomalo = True

    def procesar_ubicacion(self, viaje, lectura: LecturaGPS):
        _transicionar_segun_lectura(viaje, lectura)

    def finalizar(self, viaje):
        viaje.cambiar_a(Finalizado())


class Detenido(EstadoViaje):
    nombre = "DETENIDO"
    es_anomalo = True

    def procesar_ubicacion(self, viaje, lectura: LecturaGPS):
        _transicionar_segun_lectura(viaje, lectura)

    def finalizar(self, viaje):
        viaje.cambiar_a(Finalizado())


class Finalizado(EstadoViaje):
    nombre = "FINALIZADO"

    def procesar_ubicacion(self, viaje, lectura: LecturaGPS):
        raise ValueError("El viaje ya ha finalizado")


MAPA_ESTADOS_INICIALES = {
    "PROGRAMADO": Programado,
    "EN_RUTA": EnRuta,
    "DESVIADO": Desviado,
    "DETENIDO": Detenido,
    "FINALIZADO": Finalizado,
}