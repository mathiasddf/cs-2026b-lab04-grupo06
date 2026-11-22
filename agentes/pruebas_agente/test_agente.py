"""Pruebas unitarias del propio agente (Albada, 2025, cap. 9): contrato, política, máquina de estados y sandbox."""
import json, sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.politica import Politica
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado
from agente.nucleo import Agente, EstadoAgente

H = {"leer_archivo", "editar_archivo", "ejecutar_comando"}
H_RUTASIT = {"listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo", "ejecutar_comando"}


@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"accion": "leer_archivo"}, False),                                      # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                   # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),    # ambas formas
    ("leer_archivo(a.py)", False),                                            # texto libre, no JSON
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado


@pytest.mark.parametrize("decision, fragmento_motivo", [
    (
        {"pensamiento": "voy a aplicar parche en estrategias_eta", "accion": "aplicar_parche", "args": {"ruta": "src/consultas/estrategias_eta.py"}},
        "herramienta desconocida",
    ),
    (
        {"pensamiento": "leer archivo", "accion": "leer_archivo", "args": "src/consultas/estrategias_eta.py"},
        "'args' debe ser un objeto JSON",
    ),
    (
        {"pensamiento": "listar", "accion": "listar_archivos", "args": {}, "confianza": 0.95},
        "campos no permitidos",
    ),
    (
        {"pensamiento": "continuar", "accion": "", "args": {}},
        "herramienta desconocida",
    ),
    (
        {"pensamiento": "   ", "accion": "buscar", "args": {"texto": "eta"}},
        "falta 'pensamiento'",
    ),
    (
        {"pensamiento": "terminado", "final": 42},
        "'final' debe ser texto",
    ),
    (
        {"pensamiento": "terminado", "final": "Resuelto", "extra": True},
        "campos no permitidos",
    ),
])
def test_contrato_decisiones_invalidas_rutasit(decision, fragmento_motivo):
    ok, motivo = validar_decision(decision, H_RUTASIT)
    assert ok is False
    assert fragmento_motivo in motivo


def test_politica_bloquea_comandos_de_red_y_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert not p.evaluar("editar_archivo", {"ruta": "tests/test_x.py", "antes": "a", "despues": "b"}, 1).permitido


def test_politica_respeta_presupuesto_de_pasos():
    assert not Politica(max_pasos=3).evaluar("leer_archivo", {"ruta": "a"}, 4).permitido


def test_sandbox_impide_salir_del_directorio(tmp_path):
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).leer_archivo("../../etc/passwd")


def _ejecutar_agente_grabado(tmp_path, decisiones, politica=None):
    trayectoria = tmp_path / "trayectoria.json"
    trayectoria.write_text(json.dumps(decisiones, ensure_ascii=False), encoding="utf-8")
    traza = tmp_path / "traza.jsonl"
    workspace = tmp_path / "repo"
    workspace.mkdir(exist_ok=True)
    agente = Agente(
        nombre="ejecutor",
        modelo=ModeloGrabado(str(trayectoria)),
        herramientas=Herramientas(workspace),
        politica=politica or Politica(max_pasos=5),
        objetivo="Prueba de máquina de estados",
        traza_archivo=str(traza),
    )
    resultado = agente.ejecutar()
    return agente, resultado, traza


def test_maquina_estados_contrato_invalido_y_recuperacion(tmp_path):
    decisiones = [
        {"pensamiento": "aplicar parche directo", "accion": "aplicar_parche", "args": {"ruta": "src/consultas/estrategias_eta.py"}},
        {"pensamiento": "corrijo y cierro", "final": "Recuperado tras error de contrato"},
    ]
    agente, resultado, traza = _ejecutar_agente_grabado(tmp_path, decisiones)
    estados = [e["estado"] for e in agente.eventos]
    assert estados == [EstadoAgente.INICIO, EstadoAgente.CONTRATO_INVALIDO, EstadoAgente.FINALIZADO]
    assert agente.estado == EstadoAgente.FINALIZADO
    assert resultado == "Recuperado tras error de contrato"
    assert traza.exists()


def test_maquina_estados_esperando_aprobacion_aprobado(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    archivo = repo / "modulo.py"
    archivo.write_text("valor = -1\n", encoding="utf-8")

    politica = Politica(max_pasos=5)
    politica.aprobar_edicion = lambda args: True
    decisiones = [
        {"pensamiento": "edito archivo", "accion": "editar_archivo", "args": {"ruta": "modulo.py", "antes": "valor = -1", "despues": "valor = 0"}},
        {"pensamiento": "edición completada", "final": "Edición aprobada y aplicada"},
    ]
    agente, resultado, _ = _ejecutar_agente_grabado(tmp_path, decisiones, politica=politica)
    estados = [e["estado"] for e in agente.eventos]
    assert estados == [
        EstadoAgente.INICIO,
        EstadoAgente.ESPERANDO_APROBACION,
        EstadoAgente.OBSERVANDO,
        EstadoAgente.FINALIZADO,
    ]
    assert archivo.read_text(encoding="utf-8") == "valor = 0\n"
    assert resultado == "Edición aprobada y aplicada"


def test_maquina_estados_esperando_aprobacion_rechazado(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    archivo = repo / "modulo.py"
    archivo.write_text("valor = -1\n", encoding="utf-8")

    politica = Politica(max_pasos=5)
    politica.aprobar_edicion = lambda args: False
    decisiones = [
        {"pensamiento": "edito archivo", "accion": "editar_archivo", "args": {"ruta": "modulo.py", "antes": "valor = -1", "despues": "valor = 0"}},
        {"pensamiento": "el humano rechazó la edición", "final": "Edición cancelada por el revisor"},
    ]
    agente, resultado, _ = _ejecutar_agente_grabado(tmp_path, decisiones, politica=politica)
    estados = [e["estado"] for e in agente.eventos]
    assert estados == [
        EstadoAgente.INICIO,
        EstadoAgente.ESPERANDO_APROBACION,
        EstadoAgente.BLOQUEADO,
        EstadoAgente.FINALIZADO,
    ]
    assert archivo.read_text(encoding="utf-8") == "valor = -1\n"
    assert resultado == "Edición cancelada por el revisor"


def test_maquina_estados_limite_alcanzado(tmp_path):
    politica = Politica(max_pasos=2)
    decisiones = [
        {"pensamiento": "paso 1", "accion": "listar_archivos", "args": {}},
        {"pensamiento": "paso 2", "accion": "listar_archivos", "args": {}},
        {"pensamiento": "paso 3 excede max_pasos", "accion": "listar_archivos", "args": {}},
    ]
    agente, resultado, _ = _ejecutar_agente_grabado(tmp_path, decisiones, politica=politica)
    estados = [e["estado"] for e in agente.eventos]
    assert estados == [
        EstadoAgente.INICIO,
        EstadoAgente.OBSERVANDO,
        EstadoAgente.OBSERVANDO,
        EstadoAgente.LIMITE_ALCANZADO,
    ]
    assert agente.estado == EstadoAgente.LIMITE_ALCANZADO
    assert resultado == "(sin respuesta final)"


def test_mapa_repo_extrae_firmas_ast_y_respeta_sandbox():
    raiz_repo = pathlib.Path(__file__).parents[2]
    h = Herramientas(str(raiz_repo))
    mapa = h.mapa_repo("src/consultas")
    assert "src/consultas/proveedores_gps.py" in mapa
    assert "def normalizar_trama_gps(" in mapa
    assert "class DatosGPSIncompletosError" in mapa
    assert "src/consultas/estrategias_eta.py" in mapa
    assert "def calcular_eta_a_paradero(" in mapa

    error_inexistente = h.mapa_repo("src/no_existe_carpeta")
    assert error_inexistente.startswith("ERROR:")

    with pytest.raises(PermissionError):
        h.mapa_repo("..")


def test_memoria_notas_anotar_y_leer_notas(tmp_path):
    h = Herramientas(str(tmp_path))
    assert h.leer_notas() == "Sin notas registradas aún en notas.md."

    assert h.anotar("") == "ERROR: el texto de la nota no puede estar vacío"
    assert h.anotar("   ") == "ERROR: el texto de la nota no puede estar vacío"
    assert not (tmp_path / "notas.md").exists()

    assert h.anotar("Hipótesis: normalizar_trama_gps no valida trama None ni claves faltantes") == "OK: nota guardada en notas.md"
    assert h.anotar("Archivos revisados: issues/ISSUE-03.md, src/consultas/proveedores_gps.py") == "OK: nota guardada en notas.md"

    contenido = h.leer_notas()
    assert "- Hipótesis: normalizar_trama_gps no valida trama None ni claves faltantes" in contenido
    assert "- Archivos revisados: issues/ISSUE-03.md, src/consultas/proveedores_gps.py" in contenido


def test_catalogo_y_politica_incluyen_herramientas_e4(tmp_path):
    catalogo = Herramientas(str(tmp_path)).catalogo()
    for nombre in ("mapa_repo", "anotar", "leer_notas"):
        assert nombre in catalogo
        assert isinstance(catalogo[nombre], str) and len(catalogo[nombre]) > 20
        assert nombre in Politica().herramientas_permitidas

