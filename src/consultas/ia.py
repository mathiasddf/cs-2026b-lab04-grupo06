"""Componente de IA aislado detrás de Strategy, Adapter, Decorator (Caché) y Chain of Responsibility (Guardrails)."""
from abc import ABC, abstractmethod


class ProveedorLLM(ABC):
    """STRATEGY: puerto para intercambiar proveedores de modelos de lenguaje sin tocar el dominio."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        pass


class ClaudeAdapter(ProveedorLLM):
    """ADAPTER: adapta el cliente de Claude / LLM externo a la interfaz ProveedorLLM."""

    def __init__(self, cliente):
        self._cliente = cliente

    def completar(self, prompt: str) -> str:
        return self._cliente.generar(prompt)


class LocalLLMAdapter(ProveedorLLM):
    """ADAPTER: adapta un modelo local (Ollama / Llama.cpp) a la interfaz ProveedorLLM."""

    def __init__(self, cliente):
        self._cliente = cliente

    def completar(self, prompt: str) -> str:
        return self._cliente.generar(prompt)


class ConCacheLLM(ProveedorLLM):
    """DECORATOR: guarda respuestas a prompts idénticos para reducir latencia y costo de API."""

    def __init__(self, interno: ProveedorLLM):
        self._interno = interno
        self._cache: dict[str, str] = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]


class Guardrail(ABC):
    """CHAIN OF RESPONSIBILITY: eslabón base para validar la salida no determinista del LLM."""

    def __init__(self, siguiente: "Guardrail | None" = None):
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto = self._aplicar(texto)
        return self._siguiente.validar(texto) if self._siguiente else texto

    @abstractmethod
    def _aplicar(self, texto: str) -> str:
        pass


class SinTiemposInventados(Guardrail):
    """Bloquea respuestas donde el LLM inventa minutos de llegada contradiciendo el motor de ETA."""

    def _aplicar(self, texto: str) -> str:
        bajo = texto.lower()
        if " min" in bajo or "minutos" in bajo:
            raise ValueError("Guardrail: la IA inventó un tiempo de llegada no verificado")
        return texto


class SinAfirmacionesProhibidas(Guardrail):
    """Bloquea promesas absolutas o alarmistas no verificadas por el centro de control."""

    PROHIBIDAS = ["garantizado", "sin tráfico", "100% seguro", "accidente fatal"]

    def _aplicar(self, texto: str) -> str:
        bajo = texto.lower()
        for palabra in self.PROHIBIDAS:
            if palabra in bajo:
                raise ValueError(f"Guardrail: afirmación no permitida '{palabra}'")
        return texto


class LongitudMaximaParadero(Guardrail):
    """Garantiza que la explicación quepa en la alerta móvil y pantallas informativas del SIT."""

    def __init__(self, max_chars: int = 180, siguiente: Guardrail | None = None):
        super().__init__(siguiente)
        self._max_chars = max_chars

    def _aplicar(self, texto: str) -> str:
        if len(texto) > self._max_chars:
            raise ValueError("Guardrail: explicación demasiado larga para pantalla de paradero")
        return texto


class ExplicadorRetrasosIA:
    """Caso de uso E5 de RutaSIT: explica el motivo de un retraso a partir de eventos de la ruta."""

    def __init__(self, proveedores: dict[str, ProveedorLLM], guardrail: Guardrail | None = None):
        self._proveedores = proveedores
        self._guardrail = guardrail or SinTiemposInventados(
            SinAfirmacionesProhibidas(LongitudMaximaParadero(180))
        )

    def explicar(
        self, placa: str, estado: str, eventos_ruta: list[str], proveedor: str = "CLAUDE"
    ) -> str:
        if proveedor not in self._proveedores:
            raise ValueError(f"Proveedor LLM no soportado: {proveedor}")
        prompt = f"Explica el retraso del bus {placa} ({estado}): {', '.join(eventos_ruta)}"
        respuesta = self._proveedores[proveedor].completar(prompt)
        return self._guardrail.validar(respuesta)