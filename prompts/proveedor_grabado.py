"""Proveedor grabado determinista para evaluaciones offline en promptfoo y pytest."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

PROMPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROMPTS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.consultas.ia import ProveedorLLM  # noqa: E402


def _normalizar_texto(texto: str) -> str:
    return texto.replace("\r\n", "\n").replace("\r", "\n").strip()


def _clave_version(nombre_archivo: str) -> tuple[tuple[int, ...], str]:
    """Ordena versiones de forma descendente (ej. v3.1 antes que v3, v2, v1)."""
    sin_prefijo = nombre_archivo.lstrip("vV")
    partes: list[int] = []
    for segmento in sin_prefijo.split("."):
        try:
            partes.append(int(segmento))
        except ValueError:
            partes.append(0)
    return (tuple(partes), nombre_archivo)


def _listar_versiones(tarea_dir: Path) -> list[str]:
    if not tarea_dir.is_dir():
        return []
    candidatos = [p.stem for p in tarea_dir.glob("v*.txt") if p.is_file()]
    candidatos.sort(key=_clave_version, reverse=True)
    return candidatos


def _renderizar_plantilla(plantilla: str, vars_dict: dict[str, Any]) -> str:
    resultado = plantilla
    for clave, valor in vars_dict.items():
        patron = re.compile(r"\{\{\s*" + re.escape(str(clave)) + r"\s*\}\}")
        resultado = patron.sub(lambda _, v=str(valor): v, resultado)
    return resultado


def detectar_tarea(caso_id: str) -> str:
    """Determina la carpeta de la tarea a partir del prefijo del identificador del caso."""
    identificador = str(caso_id).strip()
    if identificador.startswith("H"):
        return "criterios"
    if identificador.startswith("C"):
        return "pruebas_eta"
    raise ValueError(f"Identificador de caso no reconocido: '{caso_id}' (se esperaba prefijo H o C)")


def detectar_version(
    prompt: str, tarea_dir: Path, vars_dict: dict[str, Any] | None = None
) -> str:
    """Detecta de forma determinista la versión del prompt comparando plantillas renderizadas o marcadores."""
    prompt_norm = _normalizar_texto(prompt)
    variables = vars_dict or {}
    versiones = _listar_versiones(tarea_dir)

    if not versiones:
        raise FileNotFoundError(f"No se encontraron plantillas v*.txt en {tarea_dir}")

    # 1) Comparación exacta tras renderizar la plantilla con las variables del caso.
    for version in versiones:
        plantilla = (tarea_dir / f"{version}.txt").read_text(encoding="utf-8")
        renderizada = _normalizar_texto(_renderizar_plantilla(plantilla, variables))
        if renderizada == prompt_norm:
            return version

    # 2) Respaldo determinista por marcadores estáticos de cada plantilla.
    coincidencias: list[tuple[int, tuple[int, ...], str]] = []
    for version in versiones:
        plantilla_norm = _normalizar_texto((tarea_dir / f"{version}.txt").read_text(encoding="utf-8"))
        fragmentos = [
            frag.strip()
            for frag in re.split(r"\{\{[^}]+\}\}", plantilla_norm)
            if frag.strip()
        ]
        if fragmentos and all(frag in prompt_norm for frag in fragmentos):
            longitud_estatica = sum(len(frag) for frag in fragmentos)
            coincidencias.append((longitud_estatica, _clave_version(version)[0], version))

    if coincidencias:
        coincidencias.sort(reverse=True)
        return coincidencias[0][2]

    raise ValueError(
        f"No se pudo detectar la versión del prompt en {tarea_dir}. "
        f"Plantillas disponibles: {versiones}"
    )


def cargar_grabacion(tarea: str, version: str, caso_id: str) -> str:
    """Lee la respuesta grabada correspondiente a (tarea, version, caso_id)."""
    ruta = PROMPTS_DIR / tarea / "grabaciones" / version / f"{caso_id}.txt"
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe la grabación esperada en {ruta}")
    return ruta.read_text(encoding="utf-8")


def call_api(
    prompt: str,
    options: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Punto de entrada estándar para proveedores Python en promptfoo."""
    ctx = context or {}
    opts = options or {}
    vars_dict = ctx.get("vars") or {}

    caso_id = vars_dict.get("id")
    if not caso_id:
        raise ValueError("Falta 'vars.id' en el contexto de promptfoo para ubicar la grabación.")

    tarea = detectar_tarea(str(caso_id))
    tarea_dir = PROMPTS_DIR / tarea

    version_config = (opts.get("config") or {}).get("version")
    version = str(version_config) if version_config else detectar_version(prompt, tarea_dir, vars_dict)

    contenido = cargar_grabacion(tarea, version, str(caso_id).strip())
    return {"output": contenido}


class ProveedorGrabadoLLM(ProveedorLLM):
    """Adapter de ProveedorLLM para usar respuestas grabadas desde Python y pytest."""

    def __init__(
        self,
        version: str | None = None,
        tarea: str | None = None,
        caso_id: str | None = None,
    ) -> None:
        self._version = version
        self._tarea = tarea
        self._caso_id = caso_id

    def completar(self, prompt: str, vars_dict: dict[str, Any] | None = None) -> str:
        """Devuelve la respuesta grabada correspondiente al prompt y/o caso configurado."""
        variables = dict(vars_dict or {})
        caso_id = variables.get("id") or self._caso_id
        if not caso_id:
            coincidencia = re.search(r"\b([HC]\d+)\b", prompt)
            if coincidencia:
                caso_id = coincidencia.group(1)
        if not caso_id:
            raise ValueError("Se requiere 'caso_id' (en constructor, vars_dict o prompt) para ProveedorGrabadoLLM.")

        tarea = self._tarea or detectar_tarea(str(caso_id))
        tarea_dir = PROMPTS_DIR / tarea
        version = self._version or detectar_version(prompt, tarea_dir, variables)
        return cargar_grabacion(tarea, version, str(caso_id).strip())
