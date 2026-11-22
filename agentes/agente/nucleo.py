"""Bucle del agente: pensar -> actuar -> observar (ReAct), modelado como máquina de estados.

Estados:
  INICIO -> DECIDIENDO -> VALIDANDO_CONTRATO -> (CONTRATO_INVALIDO | FINALIZADO | EVALUANDO_POLITICA)
  EVALUANDO_POLITICA -> (LIMITE_ALCANZADO | BLOQUEADO | ESPERANDO_APROBACION | EJECUTANDO)
  ESPERANDO_APROBACION -> (BLOQUEADO | EJECUTANDO)
  EJECUTANDO -> OBSERVANDO -> DECIDIENDO
Estados finales: FINALIZADO (respuesta final) o LIMITE_ALCANZADO (presupuesto de pasos agotado).
"""
from enum import Enum
import json, time
from agente.contrato import validar_decision


class EstadoAgente(str, Enum):
    """Estados explícitos de la máquina de estados del agente de RutaSIT Arequipa."""

    INICIO = "INICIO"
    DECIDIENDO = "DECIDIENDO"
    VALIDANDO_CONTRATO = "VALIDANDO_CONTRATO"
    CONTRATO_INVALIDO = "CONTRATO_INVALIDO"
    EVALUANDO_POLITICA = "EVALUANDO_POLITICA"
    ESPERANDO_APROBACION = "ESPERANDO_APROBACION"
    EJECUTANDO = "EJECUTANDO"
    OBSERVANDO = "OBSERVANDO"
    BLOQUEADO = "BLOQUEADO"
    LIMITE_ALCANZADO = "LIMITE_ALCANZADO"
    FINALIZADO = "FINALIZADO"


class Agente:
    def __init__(self, nombre, modelo, herramientas, politica, objetivo, traza_archivo):
        self.nombre, self.modelo, self.h, self.politica = nombre, modelo, herramientas, politica
        self.historial = [{"role": "user", "content": objetivo}]       # memoria de corto plazo
        self.traza_archivo, self.eventos = traza_archivo, []
        self.estado = EstadoAgente.INICIO

    def _registrar(self, **evento):
        evento["t"] = round(time.perf_counter() - self._t0, 3)
        evento["agente"] = self.nombre
        self.eventos.append(evento)

    def _requiere_aprobacion_humana(self, accion: str, args: dict, paso: int) -> bool:
        if self.politica.aprobar_edicion is None:
            return False
        if paso > self.politica.max_pasos or accion != "editar_archivo":
            return False
        if accion not in self.politica.herramientas_permitidas:
            return False
        ruta = args.get("ruta", "")
        return not ruta.startswith(self.politica.rutas_protegidas)

    def ejecutar(self) -> str:
        self._t0 = time.perf_counter()
        self.estado = EstadoAgente.INICIO
        self._registrar(tipo="objetivo", estado=self.estado.value, texto=self.historial[0]["content"])
        conocidas = set(self.h.catalogo())
        for paso in range(1, self.politica.max_pasos + 2):
            self.estado = EstadoAgente.DECIDIENDO
            d = self.modelo.decidir(self.historial)                       # DECIDIENDO
            self.historial.append({"role": "assistant", "content": json.dumps(d, ensure_ascii=False)})
            self.estado = EstadoAgente.VALIDANDO_CONTRATO
            ok, motivo = validar_decision(d, conocidas)                   # VALIDANDO_CONTRATO
            if not ok:
                self.estado = EstadoAgente.CONTRATO_INVALIDO
                obs = f"ERROR DE CONTRATO: {motivo}. Responda solo con el JSON del protocolo."
                self._registrar(tipo="accion", estado=self.estado.value, paso=paso, pensamiento=str(d)[:200],
                                accion="(ninguna)", args={}, observacion=obs, bloqueada=True)
            elif "final" in d:
                self.estado = EstadoAgente.FINALIZADO
                self._registrar(tipo="final", estado=self.estado.value, paso=paso, pensamiento=d["pensamiento"], texto=d["final"])
                break
            else:
                accion, args = d["accion"], d.get("args", {})
                self.estado = EstadoAgente.EVALUANDO_POLITICA
                if self._requiere_aprobacion_humana(accion, args, paso):
                    self.estado = EstadoAgente.ESPERANDO_APROBACION
                    self._registrar(tipo="aprobacion", estado=self.estado.value, paso=paso,
                                    pensamiento=d["pensamiento"], accion=accion, args=args)
                veredicto = self.politica.evaluar(accion, args, paso)     # EVALUANDO_POLITICA / ESPERANDO_APROBACION
                if veredicto.permitido:
                    self.estado = EstadoAgente.EJECUTANDO
                    try:
                        obs = getattr(self.h, accion)(**args)             # EJECUTANDO
                    except Exception as e:                                # el error también es una observación
                        obs = f"ERROR: {type(e).__name__}: {e}"
                    self.estado = EstadoAgente.OBSERVANDO
                    self._registrar(tipo="accion", estado=self.estado.value, paso=paso, pensamiento=d["pensamiento"],
                                    accion=accion, args=args, observacion=obs[:600], bloqueada=False)
                else:
                    obs = f"BLOQUEADO POR LA POLÍTICA: {veredicto.motivo}"
                    limite = "máximo" in veredicto.motivo
                    self.estado = EstadoAgente.LIMITE_ALCANZADO if limite else EstadoAgente.BLOQUEADO
                    self._registrar(tipo="accion", estado=self.estado.value, paso=paso,
                                    pensamiento=d["pensamiento"], accion=accion, args=args, observacion=obs, bloqueada=True)
                    if limite:
                        break
            self.historial.append({"role": "user", "content": f"Observación: {obs}"})   # OBSERVANDO -> DECIDIENDO
        with open(self.traza_archivo, "w", encoding="utf-8") as f:
            for e in self.eventos:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return self.eventos[-1].get("texto", "(sin respuesta final)")
