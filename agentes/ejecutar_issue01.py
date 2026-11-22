"""Ejecutor de un único agente ReAct sobre ISSUE-01 en un sandbox aislado de RutaSIT Arequipa."""
import argparse
import json
import pathlib
import shutil
import sys

DIR_AGENTES = pathlib.Path(__file__).resolve().parent
RAIZ_REPO = DIR_AGENTES.parent
sys.path.insert(0, str(DIR_AGENTES))

from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado, ModeloInteractivo
from agente.nucleo import Agente
from agente.politica import Politica

SANDBOX = DIR_AGENTES / ".sandbox" / "issue01"
TRAYECTORIA = DIR_AGENTES / "trayectorias" / "issue01_react.json"
TRAZA = DIR_AGENTES / "trazas" / "issue01_react.jsonl"


def preparar_sandbox(destino: pathlib.Path = SANDBOX) -> pathlib.Path:
    """Crea una copia limpia del repositorio (src, tests, issues, .importlinter) para el agente."""
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir(parents=True, exist_ok=True)
    ignorar = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
    for carpeta in ("src", "tests", "issues"):
        shutil.copytree(RAIZ_REPO / carpeta, destino / carpeta, ignore=ignorar)
    importlinter = RAIZ_REPO / ".importlinter"
    if importlinter.exists():
        shutil.copy2(importlinter, destino / ".importlinter")
    return destino


def construir_objetivo(herramientas: Herramientas) -> str:
    return (
        "Resuelve el reporte issues/ISSUE-01.md en el repositorio RutaSIT Arequipa.\n"
        "Responde SIEMPRE con un objeto JSON válido del protocolo:\n"
        '  {"pensamiento": "...", "accion": "<herramienta>", "args": {...}}\n'
        '  {"pensamiento": "...", "final": "<resumen final>"}\n'
        f"Herramientas disponibles: {json.dumps(herramientas.catalogo(), ensure_ascii=False)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente ReAct sobre ISSUE-01 en sandbox aislado.")
    parser.add_argument(
        "--modo",
        choices=("interactivo", "grabado"),
        default="grabado",
        help="interactivo (graba decisiones) o grabado (reproduce trayectoria determinista).",
    )
    parser.add_argument(
        "--trayectoria",
        type=pathlib.Path,
        default=TRAYECTORIA,
        help="Ruta del archivo JSON de trayectoria.",
    )
    parser.add_argument(
        "--traza",
        type=pathlib.Path,
        default=TRAZA,
        help="Ruta del archivo JSONL de traza.",
    )
    args = parser.parse_args()

    sandbox = preparar_sandbox()
    args.trayectoria.parent.mkdir(parents=True, exist_ok=True)
    args.traza.parent.mkdir(parents=True, exist_ok=True)

    herramientas = Herramientas(str(sandbox))
    modelo = (
        ModeloInteractivo(str(args.trayectoria))
        if args.modo == "interactivo"
        else ModeloGrabado(str(args.trayectoria))
    )
    politica = Politica(max_pasos=12)
    objetivo = construir_objetivo(herramientas)

    agente = Agente("ejecutor", modelo, herramientas, politica, objetivo, str(args.traza))
    resultado = agente.ejecutar()

    contexto_chars = len(json.dumps(agente.historial, ensure_ascii=False))
    pasos = [e for e in agente.eventos if e["tipo"] in ("accion", "final")]
    invalidos = sum(1 for e in agente.eventos if e.get("estado") == "CONTRATO_INVALIDO")
    print("\n=== RESULTADO AGENTE REACT (ISSUE-01) ===")
    print(resultado)
    print(
        f"[ejecutor] pasos: {len(pasos)} | CONTRATO_INVALIDO: {invalidos} | "
        f"contexto final: {contexto_chars} caracteres (~{contexto_chars // 4} tokens)"
    )


if __name__ == "__main__":
    main()
