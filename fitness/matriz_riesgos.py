"""Generador de la Matriz de Probabilidad e Impacto de riesgos ATAM-lite (E7 - RutaSIT Arequipa)."""
from __future__ import annotations
import os


def generar_matriz_riesgos(ruta_salida: str = "docs/architecture/img/matriz_riesgos.png") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.8, 5.4))

    # Zonas de fondo (Verde = aceptable, Roja = zona crítica)
    ax.add_patch(Rectangle((0.5, 0.5), 2.0, 2.0, facecolor="#E6F5EA", alpha=0.85))
    ax.add_patch(Rectangle((2.5, 2.5), 3.0, 3.0, facecolor="#FADBD8", alpha=0.85))

    ax.text(0.65, 0.65, "Zona aceptable", color="#2E8B57", fontsize=9, fontstyle="italic")
    ax.text(4.65, 5.25, "Zona crítica", color="#A61C1C", fontsize=9, fontstyle="italic", fontweight="bold")

    riesgos = [
        ("R1", 3.0, 5.0, "#B03A2E", "VPS único: punto único\nde falla (SPOF)"),
        ("R2", 2.0, 5.0, "#D4AC0D", "RLS o JWT mal configurado\nexpone telemetría entre empresas"),
        ("R3", 4.0, 4.0, "#B03A2E", "Caída de SDK GPS o Last-Known\nsolo en Redis volátil"),
        ("R4", 4.0, 3.0, "#B03A2E", "Caché Redis (TTL 10s) muestra\nETA con leve desfase"),
        ("R5", 3.0, 2.0, "#D4AC0D", "Proveedor de IA cambia tarifa\no latencia al explicar retrasos"),
    ]

    for codigo, prob, imp, color, texto in riesgos:
        ax.scatter(prob, imp, s=520, color=color, edgecolors="white", linewidth=1.8, zorder=4)
        ax.text(prob, imp, codigo, ha="center", va="center", color="white", fontweight="bold", fontsize=9.5, zorder=5)
        offset_x = 0.22 if prob < 4.3 else -1.35
        ax.text(prob + offset_x, imp, texto, va="center", fontsize=8.5, color="#222222", zorder=5)

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Probabilidad (1 = muy baja ... 5 = muy alta)")
    ax.set_ylabel("Impacto en los escenarios de calidad (1 a 5)")
    ax.set_title("Riesgos encontrados en la evaluación ATAM-lite — RutaSIT Arequipa 2.0")
    ax.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    generar_matriz_riesgos()
    print("Matriz de riesgos generada en docs/architecture/img/matriz_riesgos.png")
