#!/usr/bin/env python3
"""Compuerta de calidad para evaluaciones de prompts con promptfoo.

Verifica que los resultados de promptfoo cumplan el umbral mínimo de pase
para cada suite (criterios de aceptacion INVEST y generacion de pruebas ETA).

Uso:
    python prompts/quality_gate.py

Archivos de entrada (generados por promptfoo eval --output):
    /tmp/eval_criterios.json
    /tmp/eval_pruebas_eta.json

Codigo de salida:
    0  -> todas las suites pasan la compuerta
    1  -> al menos una suite falla o falta un archivo
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuracion de suites
# ---------------------------------------------------------------------------
SUITES = [
    {
        "nombre": "criterios",
        "archivo": Path("/tmp/eval_criterios.json"),
        "umbral_pass_rate": 0.75,  # 75 % de asserts deben pasar
    },
    {
        "nombre": "pruebas_eta",
        "archivo": Path("/tmp/eval_pruebas_eta.json"),
        "umbral_pass_rate": 0.75,
    },
]


def _leer_resultados(ruta: Path) -> dict:
    if not ruta.exists():
        print(f"[ERROR] No se encontro el archivo de evaluacion {ruta}", file=sys.stderr)
        sys.exit(1)
    with ruta.open(encoding="utf-8") as fh:
        return json.load(fh)


def _calcular_pass_rate(datos: dict) -> tuple[int, int, float]:
    """Devuelve (pasados, total, tasa) a partir del JSON de promptfoo."""
    resultados_raw = datos.get("results")

    # Formato promptfoo >= 0.73: datos["results"] es dict con "stats"
    if isinstance(resultados_raw, dict):
        stats = resultados_raw.get("stats") or {}
        if stats:
            passed = int(stats.get("successes", 0))
            failed = int(stats.get("failures", 0))
            total = passed + failed
            rate = passed / total if total > 0 else 0.0
            return passed, total, rate

        # Puede haber una lista dentro del dict bajo "results"
        lista = resultados_raw.get("results") or []
        if isinstance(lista, list) and lista:
            passed = sum(1 for r in lista if r.get("success") or r.get("passed"))
            total = len(lista)
            rate = passed / total if total > 0 else 0.0
            return passed, total, rate

    # Formato alternativo: datos["results"] es lista plana
    if isinstance(resultados_raw, list):
        passed = sum(1 for r in resultados_raw if r.get("success") or r.get("passed"))
        total = len(resultados_raw)
        rate = passed / total if total > 0 else 0.0
        return passed, total, rate

    # Formato con tabla de resultados individuales en datos["table"]["body"]
    filas = (datos.get("table") or {}).get("body") or []
    if filas:
        passed = 0
        total = 0
        for fila in filas:
            for celda in fila:
                if isinstance(celda, dict) and "pass" in celda:
                    total += 1
                    if celda["pass"]:
                        passed += 1
        rate = passed / total if total > 0 else 0.0
        return passed, total, rate

    return 0, 0, 0.0


def main() -> int:
    hay_fallo = False

    for suite in SUITES:
        nombre = suite["nombre"]
        archivo = suite["archivo"]
        umbral = suite["umbral_pass_rate"]

        print(f"\n{'=' * 60}")
        print(f"Suite: {nombre}")
        print(f"Archivo: {archivo}")

        datos = _leer_resultados(archivo)
        pasados, total, tasa = _calcular_pass_rate(datos)

        print(f"Resultados: {pasados}/{total} asserts pasaron ({tasa:.1%})")
        print(f"Umbral requerido: {umbral:.0%}")

        if total == 0:
            print(f"[ERROR] No se encontraron resultados en {archivo}", file=sys.stderr)
            hay_fallo = True
        elif tasa < umbral:
            print(
                f"[FALLO] Suite '{nombre}' no supera la compuerta "
                f"({tasa:.1%} < {umbral:.0%})",
                file=sys.stderr,
            )
            hay_fallo = True
        else:
            print(f"[OK] Suite '{nombre}' supera la compuerta ({tasa:.1%} >= {umbral:.0%})")

    print(f"\n{'=' * 60}")
    if hay_fallo:
        print("[COMPUERTA FALLIDA] Al menos una suite no cumple el umbral.", file=sys.stderr)
        return 1

    print("[COMPUERTA SUPERADA] Todas las suites cumplen el umbral de calidad.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
