#!/usr/bin/env python3
"""Compuerta de calidad (Quality Gate) para evaluaciones de prompts con promptfoo.

Verifica que la versión objetivo (producción) de cada suite alcance el 100 %
de casos aprobados (8/8), aun cuando las versiones históricas (v1, v2) fallen
intencionalmente en la comparativa.

Uso:
    python prompts/quality_gate.py
    python prompts/quality_gate.py --criterios /ruta/criterios.json --pruebas-eta /ruta/pruebas_eta.json

Codigo de salida:
    0  -> todas las suites pasan la compuerta en su versión objetivo
    1  -> al menos una suite falla o falta un archivo de evaluación
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUITES = [
    {
        "clave": "criterios",
        "nombre": "Tarea A - Criterios INVEST",
        "archivo_defecto": Path("/tmp/eval_criterios.json"),
        "version_esperada": "v3.1.txt",
        "total_esperado": 8,
    },
    {
        "clave": "pruebas_eta",
        "nombre": "Tarea B - Pruebas Pytest ETA",
        "archivo_defecto": Path("/tmp/eval_pruebas_eta.json"),
        "version_esperada": "v3.txt",
        "total_esperado": 8,
    },
]


def _es_version_objetivo(label: str, version_esperada: str) -> bool:
    if version_esperada == "v3.1.txt":
        return "v3.1.txt" in label
    if version_esperada == "v3.txt":
        return "v3.txt" in label and "v3.1" not in label
    return version_esperada in label


def verificar_evaluacion(
    ruta_archivo: Path,
    nombre_tarea: str,
    version_esperada: str,
    total_esperado: int = 8,
) -> bool:
    """Evalúa un archivo JSON de promptfoo y valida la versión objetivo al 100 %."""
    if not ruta_archivo.exists():
        print(
            f"[ERROR] No se encontro el archivo de evaluacion {ruta_archivo}",
            file=sys.stderr,
        )
        return False

    with ruta_archivo.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    prompts = data.get("results", {}).get("prompts", [])
    print("\n" + "=" * 60)
    print(f" Resumen de Evaluacion: {nombre_tarea}")
    print("=" * 60)

    if not prompts:
        print(
            f"[ERROR] El archivo {ruta_archivo} no contiene resultados de prompts.",
            file=sys.stderr,
        )
        return False

    mejor_version_encontrada = False
    mejor_version_ok = False

    for p in prompts:
        label = p.get("label") or p.get("display") or ""
        first_line = label.split("\n")[0][:75]
        metrics = p.get("metrics", {})
        passed = int(metrics.get("testPassCount", 0))
        failed = int(metrics.get("testFailCount", 0))
        errors = int(metrics.get("testErrorCount", 0))
        total = passed + failed + errors
        pct = (passed / total) * 100 if total > 0 else 0.0
        print(f" * {first_line}: {passed}/{total} ({pct:.1f} %)")

        if _es_version_objetivo(label, version_esperada):
            mejor_version_encontrada = True
            if passed == total_esperado and failed == 0 and errors == 0:
                print(
                    f"   --> GATE APROBADO: {version_esperada} alcanzo "
                    f"{passed}/{total_esperado} (100.0 %)"
                )
                mejor_version_ok = True
            else:
                print(
                    f"   --> GATE FALLIDO: {version_esperada} obtuvo "
                    f"{passed}/{total_esperado} (fallaron {failed}, errores {errors})",
                    file=sys.stderr,
                )

    if not mejor_version_encontrada:
        print(
            f"[ERROR] No se encontro la version objetivo '{version_esperada}' en {ruta_archivo}",
            file=sys.stderr,
        )
        return False

    return mejor_version_ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compuerta de calidad (Quality Gate) para evaluaciones promptfoo."
    )
    parser.add_argument(
        "--criterios",
        type=Path,
        default=SUITES[0]["archivo_defecto"],
        help="Ruta al JSON de resultados de Tarea A (criterios INVEST).",
    )
    parser.add_argument(
        "--pruebas-eta",
        dest="pruebas_eta",
        type=Path,
        default=SUITES[1]["archivo_defecto"],
        help="Ruta al JSON de resultados de Tarea B (pruebas pytest ETA).",
    )
    args = parser.parse_args(argv)

    rutas = {
        "criterios": args.criterios,
        "pruebas_eta": args.pruebas_eta,
    }

    resultados = [
        verificar_evaluacion(
            ruta_archivo=rutas[suite["clave"]],
            nombre_tarea=suite["nombre"],
            version_esperada=suite["version_esperada"],
            total_esperado=suite["total_esperado"],
        )
        for suite in SUITES
    ]

    if not all(resultados):
        print(
            "\n[FALLO] La compuerta de calidad de prompts no se cumplio.",
            file=sys.stderr,
        )
        return 1

    print(
        "\n[EXITO] Compuerta de calidad superada al 100% para Tarea A (v3.1) y Tarea B (v3)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
