"""Simulación Monte Carlo para la Iteración 2 de ADD (QA-02: Disponibilidad ante caída de SDK GPS).

Escenario simulado:
- Jornada pico con 2400 consultas de ETA hacia una concesionaria (ej. ConectaAQP).
- 6% de fallas transitorias de red (timeouts aislados).
- Una caída total del SDK GPS de la concesionaria durante 15 minutos continuos (ventanas 900 a 1300).
- Se comparan 3 modos:
  1. 'sin_tacticas': llamada directa sin reintentos ni fallback.
  2. 'reintentos': hasta 3 intentos por consulta (Lab 07), sin circuit breaker ni Last-Known persistente.
  3. 'breaker': Reintentos cortos (2) + ConCircuitBreakerGPS + Fallback a tabla Last-Known en PostgreSQL.
"""
from __future__ import annotations
import os
import random

def simular(
    modo: str,
    total_consultas: int = 2400,
    prob_falla_transitoria: float = 0.06,
    inicio_caida: int = 900,
    fin_caida: int = 1300,
    semilla: int = 42,
) -> dict[str, float | int]:
    """Ejecuta la simulación Monte Carlo de disponibilidad para el modo indicado."""
    rnd = random.Random(semilla)
    errores_500_o_sin_eta = 0
    llamadas_en_caida = 0
    respuestas_exitosas = 0

    fallas_consecutivas = 0
    abierto_hasta = -1
    umbral_breaker = 3
    ventana_espera = 25  # consultas equivalentes a 60 s de enfriamiento
    tiene_last_known_bd = True  # El bus ya venía reportando posición antes de la caída

    for i in range(total_consultas):
        en_caida_total = inicio_caida <= i < fin_caida

        def _llamar_sdk() -> bool:
            nonlocal llamadas_en_caida
            if en_caida_total:
                llamadas_en_caida += 1
                return False
            return rnd.random() >= prob_falla_transitoria

        if modo == "sin_tacticas":
            if _llamar_sdk():
                respuestas_exitosas += 1
            else:
                errores_500_o_sin_eta += 1

        elif modo == "reintentos":
            exito = False
            for _ in range(3):
                if _llamar_sdk():
                    exito = True
                    break
            if exito:
                respuestas_exitosas += 1
            else:
                errores_500_o_sin_eta += 1

        elif modo == "breaker":
            if i < abierto_hasta:
                # Circuito ABIERTO: falla rápido (0 llamadas al SDK caído) y sirve Last-Known desde PostgreSQL
                if tiene_last_known_bd:
                    respuestas_exitosas += 1
                else:
                    errores_500_o_sin_eta += 1
                continue

            # Circuito CERRADO o SEMIABIERTO: prueba hasta 2 intentos cortos
            exito = False
            for _ in range(2):
                if _llamar_sdk():
                    exito = True
                    break
            if exito:
                fallas_consecutivas = 0
                abierto_hasta = -1
                respuestas_exitosas += 1
            else:
                fallas_consecutivas += 1
                if fallas_consecutivas >= umbral_breaker or i == abierto_hasta:
                    abierto_hasta = i + ventana_espera
                # Aunque el SDK falló, responde con Last-Known Location persistida en PostgreSQL + bandera alerta
                if tiene_last_known_bd:
                    respuestas_exitosas += 1
                else:
                    errores_500_o_sin_eta += 1
        else:
            raise ValueError(f"Modo desconocido: {modo}")

    tasa_exito = round((respuestas_exitosas / total_consultas) * 100.0, 2)
    return {
        "total": total_consultas,
        "perdidos": errores_500_o_sin_eta,
        "exitosas": respuestas_exitosas,
        "tasa_exito_pct": tasa_exito,
        "llamadas_en_caida": llamadas_en_caida,
    }


def generar_grafico_iteracion2(
    ruta_salida: str = "docs/architecture/add/img/iteracion2_disponibilidad.png",
) -> dict[str, dict]:
    """Genera el gráfico comparativo de la simulación Monte Carlo para la Iteración 2 de ADD."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    modos = [
        ("Sin tácticas", "sin_tacticas", "#D9534F"),
        ("Solo Reintentos (3)", "reintentos", "#F0AD4E"),
        ("Reintentos + Circuit Breaker\n+ Last-Known en PostgreSQL", "breaker", "#2E8B57"),
    ]
    res = {clave: simular(clave) for _, clave, _ in modos}

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.5))

    etiquetas = [m[0] for m in modos]
    colores = [m[2] for m in modos]
    perdidos = [res[m[1]]["perdidos"] for m in modos]
    tasas = [res[m[1]]["tasa_exito_pct"] for m in modos]
    llamadas = [res[m[1]]["llamadas_en_caida"] for m in modos]

    b1 = ax1.bar(etiquetas, perdidos, color=colores, width=0.52)
    for barra, p, t in zip(b1, perdidos, tasas):
        ax1.text(
            barra.get_x() + barra.get_width() / 2,
            p + 15,
            f"{p} fallidas\n({t:.1f}% éxito)",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
        )
    ax1.set_ylim(0, max(perdidos) * 1.25)
    ax1.set_ylabel("Consultas ETA fallidas / sin posición")
    ax1.set_title("Consultas fallidas en hora punta (2400 consultas)")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    b2 = ax2.bar(etiquetas, llamadas, color=colores, width=0.52)
    for barra, ll in zip(b2, llamadas):
        ax2.text(
            barra.get_x() + barra.get_width() / 2,
            ll + 25,
            f"{ll}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )
    ax2.set_ylim(0, max(llamadas) * 1.20)
    ax2.set_ylabel("Llamadas al SDK GPS durante caída de 15 min")
    ax2.set_title("Protección de workers y del proveedor GPS caído")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close(fig)
    return res

if __name__ == "__main__":
    resultados = generar_grafico_iteracion2()
    print("=== RESULTADOS SIMULACIÓN MONTE CARLO — ITERACIÓN 2 ADD (QA-02: RutaSIT Arequipa) ===")
    for k, v in resultados.items():
        print(f"Modo: {k:<15} | Fallidas: {v['perdidos']:>4} | Éxito: {v['tasa_exito_pct']:>6.2f}% | Llamadas en caída: {v['llamadas_en_caida']:>4}")
    
    # Imprimir la ruta donde se guardó la imagen
    ruta_absoluta = os.path.abspath("docs/architecture/add/img/iteracion2_disponibilidad.png")
    print(f"\n[ÉXITO] Gráfico generado correctamente en: {ruta_absoluta}")