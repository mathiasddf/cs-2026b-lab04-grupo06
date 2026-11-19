"""Generador de criterios de aceptación BDD (INVEST) con validación defensiva en Capa 3."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import jsonschema

from src.consultas.ia import ProveedorLLM


class SalidaInvalida(Exception):
    """Excepción de dominio lanzada cuando la respuesta del LLM no es JSON válido o viola el esquema."""


class ProveedorGrabadoAdapter(ProveedorLLM):
    """ADAPTER: lee respuestas pregrabadas offline para evaluaciones deterministas y pruebas pytest."""

    def __init__(
        self,
        version: str = "v3.1",
        directorio_grabaciones: Path | None = None,
    ) -> None:
        self._version = version
        if directorio_grabaciones is not None:
            self._directorio = directorio_grabaciones
        else:
            self._directorio = (
                Path(__file__).resolve().parents[2] / "prompts" / "criterios" / "grabaciones"
            )

    def completar(self, prompt: str) -> str:
        """Detecta el identificador de la historia (H1-H8) y devuelve el contenido de la grabación."""
        # 1. Buscar en tags <historia id="..."> (tomando la última coincidencia distinta de H0 para evitar el ejemplo)
        coincidencias_tags = re.findall(r'<historia\s+id=["\']?([Hh]\d+)["\']?>', prompt)
        tags_validos = [m.upper() for m in coincidencias_tags if m.upper() != "H0"]
        if tags_validos:
            historia_id = tags_validos[-1]
        else:
            # 2. Buscar en formato v2 "Historia (H...):"
            coincidencias_v2 = re.findall(r'Historia\s*\(\s*([Hh]\d+)\s*\)', prompt, re.IGNORECASE)
            v2_validos = [m.upper() for m in coincidencias_v2 if m.upper() != "H0"]
            if v2_validos:
                historia_id = v2_validos[-1]
            else:
                # 3. Respaldo general buscando identificadores H1-H8 (evitando H0)
                coincidencias_gen = re.findall(r'\b([Hh][1-8])\b', prompt)
                if coincidencias_gen:
                    historia_id = coincidencias_gen[-1].upper()
                else:
                    raise ValueError(f"No se pudo identificar el ID de historia en el prompt: {prompt[:120]}...")

        ruta_archivo = self._directorio / self._version / f"{historia_id}.txt"

        if not ruta_archivo.is_file():
            raise FileNotFoundError(
                f"No existe el archivo de grabación para la versión '{self._version}' e historia '{historia_id}' en {ruta_archivo}"
            )

        return ruta_archivo.read_text(encoding="utf-8")


class GeneradorCriterios:
    """Caso de uso E6: genera y valida criterios de aceptación INVEST bajo el puerto ProveedorLLM."""

    def __init__(
        self,
        proveedor: ProveedorLLM,
        version: str = "v3.1",
        directorio_criterios: Path | None = None,
    ) -> None:
        self._proveedor = proveedor
        self._version = version
        base_dir = directorio_criterios or (
            Path(__file__).resolve().parents[2] / "prompts" / "criterios"
        )
        self._base_dir = base_dir

        ruta_plantilla = self._base_dir / f"{version}.txt"
        ruta_esquema = self._base_dir / "esquema.json"

        if not ruta_plantilla.is_file():
            raise FileNotFoundError(f"Plantilla de prompt no encontrada en {ruta_plantilla}")
        if not ruta_esquema.is_file():
            raise FileNotFoundError(f"Esquema JSON no encontrado en {ruta_esquema}")

        self._plantilla = ruta_plantilla.read_text(encoding="utf-8")
        self._esquema = json.loads(ruta_esquema.read_text(encoding="utf-8"))

    def generar(self, historia_id: str, historia: str) -> dict[str, Any]:
        """Genera y valida criterios de aceptación en formato Gherkin aplicando la Capa 3 de defensa."""
        # 1. Renderizar plantilla de prompt con variables
        prompt = self._plantilla
        for clave, valor in [("id", historia_id), ("historia", historia)]:
            patron = re.compile(r"\{\{\s*" + re.escape(clave) + r"\s*\}\}")
            prompt = patron.sub(lambda _, v=str(valor): v, prompt)

        # 2. Invocar el proveedor LLM (Strategy / Adapter / Decorator)
        respuesta = self._proveedor.completar(prompt)

        # 3. Capa 3 de defensa: Parseo JSON estricto
        try:
            criterios = json.loads(respuesta)
        except json.JSONDecodeError as exc:
            raise SalidaInvalida(
                f"La salida del LLM no es un JSON válido para la historia '{historia_id}': {exc}"
            ) from exc

        if not isinstance(criterios, dict):
            raise SalidaInvalida(
                f"La salida del LLM debe ser un objeto JSON (dict), se obtuvo {type(criterios).__name__}"
            )

        # 4. Capa 3 de defensa: Validación estricta con esquema JSON (prompts/criterios/esquema.json)
        try:
            jsonschema.validate(instance=criterios, schema=self._esquema)
        except jsonschema.ValidationError as exc:
            raise SalidaInvalida(
                f"La salida del LLM viola el contrato de esquema JSON para '{historia_id}': {exc.message}"
            ) from exc

        return criterios
