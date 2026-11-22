"""Guardrails: qué puede hacer el agente, cuántas veces y con qué aprobación."""
import difflib
import re
from dataclasses import dataclass, field


def pedir_aprobacion_edicion(args: dict, input_fn=input, print_fn=print) -> bool:
    """Humano en el circuito (HITL): muestra un diff legible y exige confirmación estricta [s/n]."""
    ruta = args.get("ruta", "(desconocida)")
    antes = args.get("antes", "")
    despues = args.get("despues", "")
    diff = list(
        difflib.unified_diff(
            antes.splitlines(),
            despues.splitlines(),
            fromfile=f"a/{ruta}",
            tofile=f"b/{ruta}",
            lineterm="",
        )
    )
    print_fn(f"\n=== SOLICITUD DE APROBACIÓN HUMANA (editar_archivo) ===")
    print_fn(f"Archivo: {ruta}")
    print_fn("\n".join(diff) if diff else "(sin diferencias visibles)")
    while True:
        respuesta = input_fn("¿Aprobar esta edición? [s/n]: ").strip().lower()
        if respuesta == "s":
            return True
        if respuesta == "n":
            return False
        print_fn("Entrada inválida: responde únicamente 's' para aprobar o 'n' para rechazar.")


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas",
        "editar_archivo", "ejecutar_comando", "mapa_repo", "anotar", "leer_notas"})
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    rutas_protegidas: tuple = ("tests/",)          # el agente no puede "arreglar" las pruebas para que pasen
    max_pasos: int = 15
    aprobar_edicion = None                          # función opcional: humano en el circuito (human-in-the-loop)

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            if ruta.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)
