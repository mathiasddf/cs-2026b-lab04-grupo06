"""Simulación M/G/c para la Iteración 1 de ADD (QA-01: Rendimiento en hora punta - RutaSIT Arequipa).

Escenario QA-01:
- 50 000 consultas de ETA en hora punta (~14 req/s promedio, ráfagas pico de 20 req/s en paraderos troncales).
- Flota ampliada de 300 a 1200 buses enviando telemetría cada 10 segundos.
- Meta: p95 del tiempo de respuesta de consultar_eta <= 1500 ms en un único VPS (4 workers Gunicorn/Uvicorn).
"""

from __future__ import annotations
import heapq
import math
import os
import random
import statistics
from typing import Callable

PRESUPUESTO_P95_MS = 1500.0  # QA-01: p95 <= 1.5 s (1500 ms)


def _lognormal(rnd: random.Random, media_s: float, sigma: float = 0.35) -> float:
    """Genera un tiempo de servicio lognormal con la media indicada en segundos."""
    mu = math.log(media_s) - 0.5 * sigma * sigma
    return rnd.lognormvariate(mu, sigma)


def bd_sin_indice_1200_buses(rnd: random.Random) -> float:
    """Sin tácticas: escaneo secuencial de telemetría histórica de 1200 buses + consulta síncrona (~210 ms)."""
    return _lognormal(rnd, media_s=0.210, sigma=0.40)


def bd_con_indice_geoespacial(rnd: random.Random) -> float:
    """Táctica 1 (Gestionar recursos / optimizar consultas): Índice compuesto (bus_id, timestamp DESC) y vista materializada de tramos en PostGIS (~38 ms por consulta)."""
    return _lognormal(rnd, media_s=0.038, sigma=0.30)


def con_cache(
    servicio_bd: Callable[[random.Random], float],
    tasa_aciertos: float = 0.85,
    latencia_redis_s: float = 0.004,
) -> Callable[[random.Random], float]:
    """Táctica 2 (Controlar demanda / caché): Caché de ETA por (paradero, ruta) en Redis con TTL de 10 s."""

    def _servicio(rnd: random.Random) -> float:
        if rnd.random() < tasa_aciertos:
            return _lognormal(rnd, media_s=latencia_redis_s, sigma=0.20)
        return latencia_redis_s + servicio_bd(rnd)

    return _servicio


def simular(
    lam: float,
    workers: int,
    servicio: Callable[[random.Random], float],
    segundos: int = 120,
    semilla: int = 7,
) -> dict[str, float]:
    """Simula una cola M/G/c con llegadas de Poisson (tasa lam req/s) y c workers."""
    rnd = random.Random(semilla)
    t, llegadas = 0.0, []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)

    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas: list[float] = []

    for a in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(a, libre)
        fin = inicio + servicio(rnd)
        heapq.heappush(libres, fin)
        respuestas.append((fin - a) * 1000.0)  # conversión a ms

    respuestas.sort()

    def p(q: float) -> float:
        return respuestas[int(q * (len(respuestas) - 1))]

    return {
        "n": len(respuestas),
        "p50": round(p(0.50), 1),
        "p95": round(p(0.95), 1),
        "media": round(statistics.mean(respuestas), 1),
    }


def generar_grafico_iteracion1(
    ruta_salida: str = "docs/architecture/add/img/iteracion1_rendimiento.png",
) -> dict:
    """Ejecuta los escenarios de carga y genera el gráfico comparativo + curva de punto de sensibilidad."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cargas = [
        ("Normal\n6 req/s", 6.0),
        ("Hora punta\n14 req/s (50k/h)", 14.0),
        ("Pico troncal\n20 req/s", 20.0),
    ]
    estrategias = [
        ("Sin tácticas (4 workers)", lambda l: simular(l, 4, bd_sin_indice_1200_buses)),
        ("Escalar a 8 workers (2 VPS)", lambda l: simular(l, 8, bd_sin_indice_1200_buses)),
        ("Índice PostGIS/compuesto", lambda l: simular(l, 4, bd_con_indice_geoespacial)),
        ("Solo Caché Redis (85%)", lambda l: simular(l, 4, con_cache(bd_sin_indice_1200_buses, 0.85))),
        ("Índice + Caché TTL 10s", lambda l: simular(l, 4, con_cache(bd_con_indice_geoespacial, 0.85))),
    ]

    resultados = {nombre: [fn(lam)["p95"] for _, lam in cargas] for nombre, fn in estrategias}

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8))

    # Panel izquierdo: Comparación de p95 en escala logarítmica
    x = range(len(cargas))
    ancho = 0.16
    colores = ["#D9534F", "#F0AD4E", "#5BC0DE", "#428BCA", "#2E8B57"]
    for idx, (nombre, _) in enumerate(estrategias):
        desplazamiento = [i + (idx - 2) * ancho for i in x]
        vals = resultados[nombre]
        barras = ax1.bar(desplazamiento, vals, width=ancho, label=nombre, color=colores[idx])
        for b, v in zip(barras, vals):
            ax1.text(
                b.get_x() + b.get_width() / 2,
                v * 1.06,
                f"{int(v)}",
                ha="center",
                va="bottom",
                fontsize=7.5,
                rotation=90 if v > 1000 else 0,
            )

    ax1.axhline(
        PRESUPUESTO_P95_MS,
        color="#222222",
        linestyle="--",
        linewidth=1.2,
        label="Meta QA-01: p95 <= 1500 ms",
    )
    ax1.set_yscale("log")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([etiqueta for etiqueta, _ in cargas])
    ax1.set_ylabel("p95 del tiempo de respuesta (ms, escala log)")
    ax1.set_title("Tácticas de rendimiento frente a la carga (RutaSIT 2.0)")
    ax1.legend(fontsize=7.5, loc="upper left")
    ax1.grid(True, which="both", axis="y", linestyle=":", alpha=0.5)

    # Panel derecho: Punto de sensibilidad de la tasa de aciertos de la caché a 20 req/s
    tasas = [i / 100.0 for i in range(0, 96, 5)]
    curva_solo_cache = [
        simular(20.0, 4, con_cache(bd_sin_indice_1200_buses, h))["p95"] for h in tasas
    ]
    curva_indice_mas_cache = [
        simular(20.0, 4, con_cache(bd_con_indice_geoespacial, h))["p95"] for h in tasas
    ]

    porcentajes = [int(h * 100) for h in tasas]
    ax2.plot(porcentajes, curva_solo_cache, "o-", color="#428BCA", label="Solo caché (sin índice)")
    ax2.plot(porcentajes, curva_indice_mas_cache, "s-", color="#2E8B57", label="Índice + caché TTL 10 s")
    ax2.axhline(
        PRESUPUESTO_P95_MS,
        color="#D9534F",
        linestyle="--",
        linewidth=1.2,
        label="Umbral QA-01 (1500 ms)",
    )
    ax2.set_yscale("log")
    ax2.set_xlabel("Tasa de aciertos de la caché Redis (%)")
    ax2.set_ylabel("p95 a 20 req/s (ms, escala log)")
    ax2.set_title("Punto de sensibilidad: tasa de aciertos de caché (20 req/s)")
    ax2.legend(fontsize=8)
    ax2.grid(True, which="both", linestyle=":", alpha=0.5)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close(fig)
    return {
        "tabla": resultados,
        "sensibilidad_0_hit": curva_solo_cache[0],
        "sensibilidad_indice_0_hit": curva_indice_mas_cache[0],
    }


if __name__ == "__main__":
    datos = generar_grafico_iteracion1()
    print("=== RESULTADOS SIMULACIÓN M/G/c — ITERACIÓN 1 ADD (QA-01: RutaSIT Arequipa) ===")
    print(f"{'Estrategia':<30} | {'Normal (6/s)':>14} | {'Hora Punta (14/s)':>18} | {'Pico (20/s)':>14}")
    print("-" * 86)
    for nombre, valores in datos["tabla"].items():
        print(f"{nombre:<30} | {valores[0]:>11.1f} ms | {valores[1]:>15.1f} ms | {valores[2]:>11.1f} ms")