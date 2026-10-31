"""Fitness functions automatizadas de atributos de calidad (E5 - Lab 08 - RutaSIT Arequipa).
Si alguien elimina el índice geoespacial, la caché, el circuit breaker o el filtro RLS, el CI falla.
"""
import pytest
from fitness.rendimiento import (
    PRESUPUESTO_P95_MS,
    simular as simular_rendimiento,
    bd_con_indice_geoespacial,
    con_cache,
)
from fitness.disponibilidad import simular as simular_disponibilidad
from src.consultas.proveedores_gps import LecturaGPS, ProveedorGPS
from src.consultas.resiliencia import ConCircuitBreakerGPS, RepositorioUltimaPosicion
from src.consultas.servicio import (
    AccesoCruzadoConcesionariaError,
    SegmentoRuta,
    ServicioConsultas,
    Viaje,
)


def test_ff03_rendimiento_hora_punta_50k_consultas():
    """FF-03 (QA-01): A 20 req/s (pico de hora punta con 1200 buses), p95 debe ser <= 1500 ms."""
    r = simular_rendimiento(
        lam=20.0,
        workers=4,
        servicio=con_cache(bd_con_indice_geoespacial, tasa_aciertos=0.85),
    )
    assert r["p95"] <= PRESUPUESTO_P95_MS, f"p95={r['p95']:.1f} ms excede presupuesto de {PRESUPUESTO_P95_MS} ms"


def test_ff04_cero_consultas_perdidas_ante_caida_gps_15_min():
    """FF-04 (QA-02): Ante caída total de 15 min del SDK GPS, 0 consultas devuelven error 500."""
    r = simular_disponibilidad("breaker")
    assert r["perdidos"] == 0


def test_ff05_circuit_breaker_protege_workers_y_proveedor_caido():
    """FF-05 (QA-02): El circuit breaker reduce en más de 5 veces las llamadas al SDK caído
    y sirve la última posición conocida desde el repositorio persistente."""
    assert (
        simular_disponibilidad("breaker")["llamadas_en_caida"]
        < simular_disponibilidad("reintentos")["llamadas_en_caida"] / 5
    )

    # Verificación directa sobre el Decorator ConCircuitBreakerGPS en código real
    class ProveedorCaido(ProveedorGPS):
        def __init__(self):
            self.llamadas = 0

        def obtener_lectura(self, identificador: str) -> LecturaGPS:
            self.llamadas += 1
            raise TimeoutError("Concesionaria sin respuesta")

    reloj_falso = [100.0]
    repo = RepositorioUltimaPosicion()
    repo.guardar("V5A-789", LecturaGPS(-16.409, -71.537, 28.0, 5, True), instante=90.0)
    interno = ProveedorCaido()
    cb = ConCircuitBreakerGPS(interno, repositorio=repo, umbral_fallas=3, espera_s=60.0, reloj=lambda: reloj_falso[0])

    for _ in range(6):
        lectura = cb.obtener_lectura("V5A-789")
        assert lectura.velocidad_kmh == 28.0

    assert cb.estado == "ABIERTO"
    # Aunque se hicieron 6 consultas, el SDK caído solo recibió 3 llamadas antes de abrir el circuito
    assert interno.llamadas == 3


def test_ff06_aislamiento_multiconcesionaria_cero_fugas():
    """FF-06 (QA-04): Una concesionaria A jamás puede inyectar ni leer telemetría de la concesionaria B."""
    s = ServicioConsultas()
    v_conecta = Viaje("V-101", "V5A-789", "CONECTA", "EN_RUTA", [SegmentoRuta("Av. Ejército", 4.0)])
    v_cayma = Viaje("V-202", "V8B-123", "TRANSCAYMA", "EN_RUTA", [SegmentoRuta("Av. Cayma", 5.0)])
    lectura_ok = LecturaGPS(-16.40, -71.53, 30.0, 4, True)

    s.registrar_telemetria_operador("CONECTA", v_conecta, lectura_ok)
    s.registrar_telemetria_operador("TRANSCAYMA", v_cayma, lectura_ok)

    # Intento de suplantación: CONECTA intenta escribir sobre un bus de TRANSCAYMA
    with pytest.raises(AccesoCruzadoConcesionariaError):
        s.registrar_telemetria_operador("CONECTA", v_cayma, lectura_ok)

    # Verificación RLS: al consultar como CONECTA, obtiene 0 filas de TRANSCAYMA
    filas_conecta = s.consultar_telemetria_concesionaria("CONECTA")
    assert len(filas_conecta) == 1
    assert all(f["concesionaria_id"] == "CONECTA" for f in filas_conecta)