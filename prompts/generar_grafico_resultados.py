"""Genera el gráfico de resultados de evaluación de prompts (Lab 09) en alta resolución.

Salida: prompts/img/resultados_prompts_lab09.png (dpi=200)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def formatear_pct(valor: float) -> str:
    """Formatea porcentaje sin decimales redundantes para enteros y con 1 decimal para fracciones."""
    if abs(valor - round(valor)) < 1e-9:
        return f"{int(round(valor))}%"
    return f"{valor:.1f}%"


def main() -> None:
    raiz = Path(__file__).resolve().parent
    salida = raiz / "img" / "resultados_prompts_lab09.png"
    salida.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#CCCCCC",
            "axes.linewidth": 0.9,
            "grid.color": "#E6E6E6",
            "grid.linestyle": "--",
            "grid.linewidth": 0.7,
        }
    )

    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(16.5, 6.4),
        dpi=200,
        gridspec_kw={"width_ratios": [1.0, 1.45]},
    )
    fig.patch.set_facecolor("white")

    # =========================================================================
    # PANEL IZQUIERDO: Tasa de aprobación global (%) por versión
    # =========================================================================
    versiones = ["v1", "v2", "v3", "v3.1"]
    tarea_a = [0.0, 25.0, 87.5, 100.0]
    tarea_b = [0.0, 37.5, 100.0, None]  # Tarea B alcanzó 100% en v3

    x_left = np.arange(len(versiones))
    ancho_left = 0.34

    pos_a = [x_left[0] - ancho_left / 2, x_left[1] - ancho_left / 2, x_left[2] - ancho_left / 2, x_left[3]]
    pos_b = [x_left[0] + ancho_left / 2, x_left[1] + ancho_left / 2, x_left[2] + ancho_left / 2]
    vals_b = [v for v in tarea_b if v is not None]

    color_a = "#1F6FA8"
    color_b = "#2E9E5B"

    barras_a = ax1.bar(
        pos_a,
        tarea_a,
        width=ancho_left,
        color=color_a,
        edgecolor="#164E78",
        linewidth=0.8,
        label="Tarea A: Criterios INVEST (prompts/criterios/)",
        zorder=3,
    )
    barras_b = ax1.bar(
        pos_b,
        vals_b,
        width=ancho_left,
        color=color_b,
        edgecolor="#1E6E3E",
        linewidth=0.8,
        label="Tarea B: Pruebas ETA pytest (prompts/pruebas_eta/)",
        zorder=3,
    )

    # Línea de meta mínima 85%
    ax1.axhline(
        85.0,
        color="#C9302C",
        linestyle="--",
        linewidth=1.5,
        label="Meta mínima de aprobación (85 %)",
        zorder=4,
    )

    # Etiquetas numéricas sobre barras (Panel izquierdo)
    for barra, val in zip(barras_a, tarea_a):
        ax1.text(
            barra.get_x() + barra.get_width() / 2,
            val + 2.0,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8.8,
            fontweight="bold",
            color="#164E78",
            zorder=5,
        )

    for barra, val in zip(barras_b, vals_b):
        ax1.text(
            barra.get_x() + barra.get_width() / 2,
            val + 2.0,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8.8,
            fontweight="bold",
            color="#1E6E3E",
            zorder=5,
        )

    ax1.set_title(
        "Tasa de aprobación global por versión",
        fontsize=12.5,
        fontweight="bold",
        color="#1A2530",
        pad=12,
    )
    ax1.set_xlabel("Versión del prompt", fontsize=10.5, color="#333333", labelpad=8)
    ax1.set_ylabel("Tasa de aprobación (%)", fontsize=10.5, color="#333333")
    ax1.set_xticks(x_left)
    ax1.set_xticklabels(
        ["v1\n(base)", "v2\n(contexto+JSON)", "v3\n(patrones)", "v3.1\n(red team)"],
        fontsize=9.3,
        color="#222222",
    )
    ax1.set_ylim(0, 122)
    ax1.set_yticks(range(0, 101, 20))
    ax1.yaxis.grid(True, zorder=0)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(
        loc="upper left",
        fontsize=8.4,
        frameon=True,
        facecolor="white",
        edgecolor="#DDDDDD",
        framealpha=0.95,
    )

    # =========================================================================
    # PANEL DERECHO: Tasa de aprobación por aserción (Tarea A: v1..v3.1)
    # =========================================================================
    aserciones = [
        "A1_contrato_json",
        "A2_exito_y_error",
        "A3_sin_implementacion",
        "A4_rechaza_no_invest",
        "A5_resiste_inyeccion",
    ]
    etiquetas_x = [
        "A1_contrato\n_json\n(n=8)",
        "A2_exito\n_y_error\n(n=8)",
        "A3_sin_\nimplementacion\n(n=8)",
        "A4_rechaza\n_no_invest\n(n=2)",
        "A5_resiste\n_inyeccion\n(n=1)",
    ]

    datos_aserciones = {
        "v1": [0.0, 0.0, 12.5, 0.0, 0.0],
        "v2": [75.0, 62.5, 87.5, 0.0, 0.0],
        "v3": [100.0, 100.0, 87.5, 100.0, 100.0],
        "v3.1": [100.0, 100.0, 100.0, 100.0, 100.0],
    }

    colores_v = {
        "v1": ("#D9534F", "#A93835"),
        "v2": ("#F0AD4E", "#BD7E25"),
        "v3": ("#2B7BBA", "#1C5685"),
        "v3.1": ("#2E9E5B", "#1E6E3E"),
    }

    x_right = np.arange(len(aserciones))
    ancho_right = 0.185
    paso_right = 0.205
    offsets = [-1.5 * paso_right, -0.5 * paso_right, 0.5 * paso_right, 1.5 * paso_right]

    for (ver, valores), offset in zip(datos_aserciones.items(), offsets):
        facecolor, edgecolor = colores_v[ver]
        barras = ax2.bar(
            x_right + offset,
            valores,
            width=ancho_right,
            color=facecolor,
            edgecolor=edgecolor,
            linewidth=0.75,
            label=f"Tarea A — {ver}",
            zorder=3,
        )
        for idx, (barra, val) in enumerate(zip(barras, valores)):
            desplazamiento_y = 2.0
            # Evitar cercanía visual entre etiquetas idénticas de 4-5 caracteres contiguas
            if ver == "v3" and idx == 2:  # A3: v2=87.5% y v3=87.5%
                desplazamiento_y = 5.2
            ax2.text(
                barra.get_x() + barra.get_width() / 2,
                val + desplazamiento_y,
                formatear_pct(val),
                ha="center",
                va="bottom",
                fontsize=7.2,
                fontweight="bold",
                color=edgecolor,
                zorder=5,
            )

    ax2.set_title(
        "Tasa de aprobación por aserción — Tarea A (v1 a v3.1)",
        fontsize=12.5,
        fontweight="bold",
        color="#1A2530",
        pad=12,
    )
    ax2.set_xlabel("Aserción automatizada (promptfoo)", fontsize=10.5, color="#333333", labelpad=8)
    ax2.set_ylabel("Tasa de aprobación (%)", fontsize=10.5, color="#333333")
    ax2.set_xticks(x_right)
    ax2.set_xticklabels(etiquetas_x, fontsize=8.8, color="#222222")
    ax2.set_ylim(0, 122)
    ax2.set_yticks(range(0, 101, 20))
    ax2.yaxis.grid(True, zorder=0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 0.99),
        ncol=4,
        fontsize=8.6,
        frameon=True,
        facecolor="white",
        edgecolor="#DDDDDD",
        framealpha=0.95,
    )

    fig.suptitle(
        "Evaluación de Prompts — RutaSIT Arequipa (Lab 09)",
        fontsize=15.0,
        fontweight="bold",
        color="#111A22",
        y=0.98,
    )

    fig.tight_layout(rect=(0.0, 0.01, 1.0, 0.93))
    fig.savefig(salida, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"Gráfico generado correctamente en: {salida} ({salida.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
