"""Arma el informe PDF a partir de docs/informe/informe.md y la evidencia de outputs/.

Marcadores que reemplaza (cada uno en su propia línea, salvo {{valor}} y {{json}}):

  {{tabla:<script>/<id>;cols=a,b;titulos=A,B;n=10;dec=3;vec=6;claves=min,max}}
      Tabla markdown desde outputs/resultados/<script>/<id>.csv.
      cols/titulos: columnas a mostrar y su encabezado. n: máximo de filas.
      dec: decimales para los floats. vec: cuántas componentes mostrar de un vector.
      claves: para celdas que son un dict JSON, qué claves mostrar.
  {{valor:<script>/<id>;col=<columna>;fila=0;dec=2;crudo=1}}
      Valor suelto de un CSV (en línea). crudo=1: sin formato. En {{tabla}}, crudas=col1,col2.
  {{json:<script>/<id>;ruta=a.b.c;dec=2}}
      Valor suelto del .json del paso (ruta con puntos; índices numéricos permitidos).
  {{cociente:<script>/<idA>;<script>/<idB>;ruta=a.b;dec=1}}
      Cociente A/B de un mismo valor de los .json de dos pasos (p. ej. factor de mejora).
  {{plan:<id>;ancho=0.9;titulo=...}}
      Imagen: outputs/capturas/<id>.png (o <id>_a.png, <id>_b.png) si el grupo la sacó;
      si no, el render de respaldo outputs/planes/<id>.png, marcado como tal.
  {{captura:<id>;ancho=0.9;titulo=...|<especificación de tabla de respaldo>}}
      Captura del grupo si existe; si no, la tabla de respaldo (mismo formato que {{tabla:...}}).
  {{imagen:<ruta relativa a la raíz>;ancho=0.6;titulo=...}}

Compila con pandoc + xelatex en una carpeta temporal con ruta ASCII (la ruta del proyecto
tiene espacios y 'ñ', que LaTeX no maneja bien) y verifica que el PDF tenga <= 8 páginas.

Uso: python -m src.tp2.build_informe [--max-paginas 8]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .conexion import RAIZ

FUENTE = RAIZ / "docs" / "informe" / "informe.md"
SALIDA = RAIZ / "outputs" / "informe"
RESULTADOS = RAIZ / "outputs" / "resultados"
CAPTURAS = RAIZ / "outputs" / "capturas"
PLANES = RAIZ / "outputs" / "planes"
PDF_FINAL = SALIDA / "TP2_Trabajo2_informe.pdf"

MARCADOR = re.compile(r"\{\{(tabla|valor|json|cociente|plan|captura|imagen|vectores):([^}]*)\}\}")


# LaTeX básico: sin fuentes del sistema (sirve con pdflatex, xelatex y tectonic).
# Solo se declaran los pocos símbolos Unicode que el texto usa y LaTeX no trae en modo texto.
CABECERA = r"""
\usepackage{iftex}
\ifPDFTeX
  \DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
  \DeclareUnicodeCharacter{2248}{\ensuremath{\approx}}
  \DeclareUnicodeCharacter{2265}{\ensuremath{\geq}}
\else
  \usepackage{newunicodechar}
  \newunicodechar{→}{\ensuremath{\rightarrow}}
  \newunicodechar{≈}{\ensuremath{\approx}}
  \newunicodechar{≥}{\ensuremath{\geq}}
\fi
"""


CM_POR_PX = 0.011     # escala común de las capturas en el PDF
ANCHO_MAX_CM = 17.5   # ancho útil de la página (A4/Letter con márgenes de 1,7 cm)


class Faltante(Exception):
    pass


def opciones(spec: str) -> tuple[str, dict[str, str]]:
    partes = [p.strip() for p in spec.split(";")]
    objetivo, resto = partes[0], partes[1:]
    ops = {}
    for p in resto:
        if "=" in p:
            k, v = p.split("=", 1)
            ops[k.strip()] = v.strip()
    return objetivo, ops


def num_es(x: float, dec: int) -> str:
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def formatear(valor: str, ops: dict[str, str]) -> str:
    dec = int(ops.get("dec", 3))
    if valor == "":
        return ""
    if valor in ("True", "False"):  # booleanos tal como los escribe el CSV de Python
        return "sí" if valor == "True" else "no"
    try:
        dato = json.loads(valor)
    except (json.JSONDecodeError, TypeError):
        dato = valor
    if isinstance(dato, bool):
        return "sí" if dato else "no"
    if isinstance(dato, int):
        return num_es(dato, 0)
    if isinstance(dato, float):
        return num_es(dato, dec)
    if isinstance(dato, list):
        k = int(ops.get("vec", 6))
        if all(isinstance(v, (int, float)) for v in dato):
            cuerpo = ", ".join(num_es(float(v), dec) for v in dato[:k])
            return f"[{cuerpo}{', …' if len(dato) > k else ''}] (dim {len(dato)})"
        return ", ".join(str(v) for v in dato)
    if isinstance(dato, dict):
        claves = [c for c in ops.get("claves", "").split(",") if c] or list(dato)
        return "; ".join(f"{c}: {formatear(json.dumps(dato.get(c)), ops)}" for c in claves if c in dato)
    return str(dato)


def leer_csv(objetivo: str) -> list[dict[str, str]]:
    ruta = RESULTADOS / f"{objetivo}.csv"
    if not ruta.exists():
        raise Faltante(f"no existe {ruta.relative_to(RAIZ)}")
    with ruta.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def tabla(spec: str) -> str:
    objetivo, ops = opciones(spec)
    filas = leer_csv(objetivo)
    cols = [c for c in ops.get("cols", "").split(",") if c] or (list(filas[0]) if filas else [])
    titulos = [t for t in ops.get("titulos", "").split(",") if t] or cols
    n = int(ops.get("n", len(filas)))
    crudas = set(ops.get("crudas", "").split(","))  # columnas sin formato (p. ej. años)
    var = ops.get("var")  # var=v agrega una columna con la referencia v_1, v_2, ... (ver {{vectores}})
    if var:
        titulos = titulos + [ops.get("vartitulo", "Vector")]
    lineas = ["| " + " | ".join(titulos) + " |", "|" + "|".join("---" for _ in titulos) + "|"]
    for i, f in enumerate(filas[:n], 1):
        celdas = [(f.get(c, "") if c in crudas else formatear(f.get(c, ""), ops)).replace("|", "\\|")
                  for c in cols]
        if var:
            celdas.append(rf"$\mathbf{{{var}}}_{{{i}}}$")
        lineas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def vectores(spec: str) -> str:
    """{{vectores:<script>/<id>;col=embedding;etiqueta=nodo;var=v;dec=3}}

    Lista los vectores completos, en letra chica, con la misma referencia v_1, v_2, ... que la
    columna que agrega {{tabla:...;var=v}} (mismo orden de filas que el CSV).
    """
    objetivo, ops = opciones(spec)
    filas = leer_csv(objetivo)
    dec, col, et, var = int(ops.get("dec", 3)), ops.get("col", "embedding"), ops.get("etiqueta", "nodo"), ops.get("var", "v")
    lineas = [r"\begin{footnotesize}\sloppy"]
    for i, f in enumerate(filas, 1):
        v = json.loads(f[col])
        nombre = f[et]
        for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                     ("_", r"\_"), ("{", r"\{"), ("}", r"\}")):
            nombre = nombre.replace(a, b)
        nums = "; ".join(num_es(float(x), dec) for x in v)
        lineas.append(rf"\noindent$\mathbf{{{var}}}_{{{i}}}$ ({nombre}, dim {len(v)}) $=$ [{nums}]\par\smallskip")
    lineas.append(r"\end{footnotesize}")
    return "\n".join(lineas)


def valor(spec: str) -> str:
    objetivo, ops = opciones(spec)
    filas = leer_csv(objetivo)
    fila = filas[int(ops.get("fila", 0))]
    celda = fila[ops["col"]]
    if "ruta" in ops:  # navegar dentro de una celda JSON (p. ej. modelSelectionStats)
        dato: Any = json.loads(celda)
        for parte in ops["ruta"].split("."):
            dato = dato[int(parte)] if isinstance(dato, list) else dato[parte]
        celda = json.dumps(dato)
    return celda if ops.get("crudo") else formatear(celda, ops)


def dato_json(objetivo: str, ruta_claves: str) -> Any:
    ruta = RESULTADOS / f"{objetivo}.json"
    if not ruta.exists():
        raise Faltante(f"no existe {ruta.relative_to(RAIZ)}")
    dato: Any = json.loads(ruta.read_text(encoding="utf-8"))
    for parte in ruta_claves.split("."):
        dato = dato[int(parte)] if isinstance(dato, list) else dato[parte]
    return dato


def valor_json(spec: str) -> str:
    objetivo, ops = opciones(spec)
    return formatear(json.dumps(dato_json(objetivo, ops["ruta"])), ops)


def cociente(spec: str) -> str:
    partes = [p.strip() for p in spec.split(";")]
    a, b = partes[0], partes[1]
    _, ops = opciones(";".join(["_"] + partes[2:]))
    va, vb = float(dato_json(a, ops["ruta"])), float(dato_json(b, ops["ruta"]))
    return num_es(va / vb, int(ops.get("dec", 1)))


def capturas_de(id_: str) -> list[Path]:
    unica = CAPTURAS / f"{id_}.png"
    if unica.exists():
        return [unica]
    return sorted(CAPTURAS.glob(f"{id_}_[a-z].png"))


class Imagenes:
    """Copia las imágenes a la carpeta de compilación con nombres ASCII."""

    def __init__(self, destino: Path):
        self.destino = destino
        self.n = 0
        self.uso: list[tuple[str, str]] = []

    def agregar(self, origen: Path, ancho: str, titulo: str, alto: str | None = None) -> str:
        """Solo se fija el ancho (nunca el alto), así LaTeX conserva la proporción y no estira la imagen.

        Para las capturas (PNG) el ancho sale de sus píxeles con una escala común (CM_POR_PX), de modo que
        la letra tenga el mismo tamaño en todas; se topa en ANCHO_MAX_CM. `ancho` y `alto` quedan como
        parámetros por compatibilidad con los marcadores, pero no se usan para las capturas.
        """
        self.n += 1
        nombre = f"img{self.n:02d}{origen.suffix.lower()}"
        shutil.copy(origen, self.destino / nombre)
        try:
            from PIL import Image
            with Image.open(origen) as im:
                cm = min(im.size[0] * CM_POR_PX, ANCHO_MAX_CM)
            tam = f"width={cm:.1f}cm"
        except Exception:
            tam = f"width={float(ancho) * 100:.0f}%"
        return f"![{titulo}]({nombre}){{{tam}}}"


def plan(spec: str, imgs: Imagenes) -> str:
    id_, ops = opciones(spec)
    ancho, titulo = ops.get("ancho", "0.9"), ops.get("titulo", id_)
    reales = capturas_de(id_)
    if reales:
        imgs.uso.append((id_, "captura"))
        return "\n\n".join(imgs.agregar(p, ancho, titulo, ops.get("alto", "5.5cm")) for p in reales)
    respaldo = PLANES / f"{id_}.png"
    if not respaldo.exists():
        raise Faltante(f"no hay captura ni render para {id_}")
    imgs.uso.append((id_, "render"))
    return imgs.agregar(respaldo, ancho, f"{titulo} (render de respaldo generado con el driver)")


def captura(spec: str, imgs: Imagenes) -> str:
    principal, _, respaldo = spec.partition("|")
    id_, ops = opciones(principal)
    reales = capturas_de(id_)
    if reales:
        imgs.uso.append((id_, "captura"))
        return "\n\n".join(imgs.agregar(p, ops.get("ancho", "0.9"), ops.get("titulo", id_), ops.get("alto", "4.5cm"))
                           for p in reales)
    imgs.uso.append((id_, "tabla"))
    return f"*{ops.get('titulo', id_)} (tabla de respaldo; falta la captura de Query):*\n\n{tabla(respaldo)}"


def imagen(spec: str, imgs: Imagenes) -> str:
    ruta, ops = opciones(spec)
    origen = RAIZ / ruta
    if not origen.exists():
        raise Faltante(f"no existe {ruta}")
    return imgs.agregar(origen, ops.get("ancho", "0.6"), ops.get("titulo", ""))


def contar_paginas(pdf: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(pdf)).pages)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-paginas", type=int, default=8)
    ap.add_argument("--motor", default="xelatex", help="motor LaTeX para pandoc (xelatex, tectonic...)")
    ap.add_argument("--tex", action="store_true", help="además guarda outputs/informe/tex/informe.tex con sus imágenes")
    args = ap.parse_args(argv)

    SALIDA.mkdir(parents=True, exist_ok=True)
    texto = FUENTE.read_text(encoding="utf-8")
    faltantes: list[str] = []

    with tempfile.TemporaryDirectory(prefix="tp2_informe_") as tmp:
        build = Path(tmp)
        imgs = Imagenes(build)

        def reemplazar(m: re.Match) -> str:
            tipo, spec = m.group(1), m.group(2)
            try:
                if tipo == "tabla":
                    return tabla(spec)
                if tipo == "valor":
                    return valor(spec)
                if tipo == "json":
                    return valor_json(spec)
                if tipo == "cociente":
                    return cociente(spec)
                if tipo == "vectores":
                    return vectores(spec)
                if tipo == "plan":
                    return plan(spec, imgs)
                if tipo == "captura":
                    return captura(spec, imgs)
                return imagen(spec, imgs)
            except (Faltante, KeyError, IndexError) as exc:
                faltantes.append(f"{m.group(0)} -> {exc}")
                return f"**[FALTA: {m.group(0)}]**"

        resultado = MARCADOR.sub(reemplazar, texto)
        (SALIDA / "informe_build.md").write_text(resultado, encoding="utf-8")
        (build / "informe.md").write_text(resultado, encoding="utf-8")

        if faltantes:
            print("Marcadores sin resolver:", *faltantes, sep="\n  ", file=sys.stderr)
            return 1

        (build / "cabecera.tex").write_text(CABECERA, encoding="utf-8")
        variables = [
            "-H", "cabecera.tex",
            "-V", "geometry:margin=1.7cm",
            "-V", "fontsize=10pt",
            "-V", "lang=es",
            "-V", "colorlinks=true",
            "-V", "tables=true",
        ]
        if args.tex:
            destino_tex = SALIDA / "tex"
            if destino_tex.exists():
                shutil.rmtree(destino_tex)
            destino_tex.mkdir(parents=True)
            subprocess.run(["pandoc", "informe.md", "-s", "-o", "informe.tex", *variables],
                           cwd=build, check=True, encoding="utf-8", errors="replace")
            for f in build.glob("informe.tex"):
                shutil.copy(f, destino_tex / f.name)
            for f in build.glob("img*.png"):
                shutil.copy(f, destino_tex / f.name)
        cmd = ["pandoc", "informe.md", "-o", "informe.pdf", f"--pdf-engine={args.motor}", *variables]
        proc = subprocess.run(cmd, cwd=build, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            return proc.returncode
        shutil.copy(build / "informe.pdf", PDF_FINAL)

    paginas = contar_paginas(PDF_FINAL)
    resumen_uso = ", ".join(f"{i}={u}" for i, u in imgs.uso)
    print(f"PDF: {PDF_FINAL.relative_to(RAIZ)} | páginas: {paginas} | imágenes: {resumen_uso or 'ninguna'}")
    if paginas > args.max_paginas:
        print(f"ERROR: el informe tiene {paginas} páginas (máximo {args.max_paginas}).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
