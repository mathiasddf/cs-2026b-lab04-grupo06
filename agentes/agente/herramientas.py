"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox)."""
import ast, pathlib, subprocess, re, sys, shutil


class Herramientas:
    def __init__(self, raiz: str):
        self.raiz = pathlib.Path(raiz).resolve()

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        return {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "ejecutar_pruebas": "ejecutar_pruebas(): ejecuta pytest y devuelve el resumen",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión original",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
            "mapa_repo": (
                "mapa_repo(subruta: str = 'src') -> str: analiza con AST los archivos .py "
                "bajo 'subruta' (dentro del sandbox) y devuelve un mapa compacto con clases, "
                "firmas de funciones/métodos y números de línea, o un mensaje de error si falla"
            ),
            "anotar": (
                "anotar(texto: str) -> str: guarda una nota no vacía como viñeta al final de "
                "notas.md en la raíz del sandbox (memoria de notas) y devuelve confirmación o error"
            ),
            "leer_notas": (
                "leer_notas() -> str: devuelve el contenido actual de notas.md en el sandbox, "
                "o un mensaje indicando que aún no hay notas registradas"
            ),
        }

    # --- herramientas ---
    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(p.relative_to(self.raiz).as_posix() for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz).as_posix()}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def ejecutar_pruebas(self):
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
                           cwd=self.raiz, capture_output=True, text=True, timeout=120)
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self, original="../trabajo_original"):
        import difflib
        base, salida = self._ruta_libre(original), []
        for p in sorted(self.raiz.rglob("*.py")):
            rel = p.relative_to(self.raiz); q = base / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida += difflib.unified_diff(a, p.read_text(encoding="utf-8").splitlines(),
                                           f"a/{rel}", f"b/{rel}", lineterm="", n=1)
        return "\n".join(salida) or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        cmd = comando
        if cmd.startswith("python -m pytest"):
            cmd = f'"{sys.executable}"' + cmd[len("python"):]
        elif cmd.startswith("radon ") and shutil.which("radon") is None:
            cmd = f'"{sys.executable}" -m radon ' + cmd[len("radon "):]
        elif cmd.startswith("lint-imports") and shutil.which("lint-imports") is None:
            cmd = f'"{sys.executable}" -c "from importlinter.cli import lint_imports_command; lint_imports_command()"'
        r = subprocess.run(cmd, shell=True, cwd=self.raiz, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()[-2000:]

    def _firma_funcion(self, nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        prefijo = "async def" if isinstance(nodo, ast.AsyncFunctionDef) else "def"
        params = ast.unparse(nodo.args)
        retorno = f" -> {ast.unparse(nodo.returns)}" if nodo.returns is not None else ""
        return f"L{nodo.lineno}: {prefijo} {nodo.name}({params}){retorno}"

    def mapa_repo(self, subruta: str = "src") -> str:
        base = self._ruta(subruta)
        if not base.exists():
            return f"ERROR: la ruta '{subruta}' no existe en el sandbox"
        archivos = [base] if base.is_file() and base.suffix == ".py" else sorted(
            p for p in base.rglob("*.py") if "__pycache__" not in p.parts
        )
        if not archivos:
            return f"(sin archivos .py en '{subruta}')"
        salida = []
        for archivo in archivos:
            rel = archivo.relative_to(self.raiz).as_posix()
            try:
                arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=rel)
            except (SyntaxError, UnicodeDecodeError, OSError) as exc:
                salida.append(f"{rel}\n  ERROR al parsear: {exc}")
                continue
            entradas = []
            for nodo in arbol.body:
                if isinstance(nodo, ast.ClassDef):
                    entradas.append(f"  L{nodo.lineno}: class {nodo.name}")
                    for hijo in nodo.body:
                        if isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            entradas.append(f"    {self._firma_funcion(hijo)}")
                elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    entradas.append(f"  {self._firma_funcion(nodo)}")
            if entradas:
                salida.append("\n".join([rel] + entradas))
            else:
                salida.append(f"{rel}\n  (sin clases ni funciones de nivel superior)")
        return "\n".join(salida)

    def anotar(self, texto: str) -> str:
        if not isinstance(texto, str) or not texto.strip():
            return "ERROR: el texto de la nota no puede estar vacío"
        archivo_notas = self._ruta("notas.md")
        entrada = f"- {texto.strip()}\n"
        if archivo_notas.exists():
            contenido = archivo_notas.read_text(encoding="utf-8")
            separador = "" if (not contenido or contenido.endswith("\n")) else "\n"
            archivo_notas.write_text(contenido + separador + entrada, encoding="utf-8")
        else:
            archivo_notas.write_text("# Notas de trabajo del agente\n\n" + entrada, encoding="utf-8")
        return "OK: nota guardada en notas.md"

    def leer_notas(self) -> str:
        archivo_notas = self._ruta("notas.md")
        if not archivo_notas.exists():
            return "Sin notas registradas aún en notas.md."
        return archivo_notas.read_text(encoding="utf-8").strip()
