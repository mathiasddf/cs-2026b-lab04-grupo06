"""Simuladores de servicios externos de GPS y LLM para la versión inicial (Antes del refactor)."""

class GpsConectaSDK:
    """SDK del proveedor GPS Conecta."""
    def obtener_telemetria(self, placa: str) -> dict:
        return {"speed_kmh": 25.0, "age_sec": 10, "en_corredor": True}


class GpsTransCaymaClient:
    """Cliente del proveedor GPS TransCayma."""
    def fetch_position(self, viaje_id: str) -> tuple:
        return 200, {"vel_ms": 7.0, "seconds_ago": 15, "off_route": False}


class ClienteLLMFalso:
    """Simulador de respuestas del LLM para explicaciones de retrasos."""
    def generar(self, prompt: str) -> str:
        return "El autobús presenta una ligera demora debido al tráfico habitual en la zona."


# Aliases de compatibilidad por si se requieren en otros módulos
SDKGPSSIT = GpsConectaSDK
SDKGPSMunicipal = GpsTransCaymaClient