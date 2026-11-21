"""Arma el zip de entrega del TP2 (Trabajo 2) con exactamente lo que pide la consigna.

Contenido:
    cypher/00_parte_comun.cypher, 01_ejercicio1.cypher, 02_ejercicio2.cypher, 03_ejercicio3.cypher
    notebook/ej3_4_pairre.ipynb          (ejecutado, con salidas)
    informe/TP2_Trabajo2_informe.pdf

Uso: python -m src.tp2.armar_entrega
"""
from __future__ import annotations

import json
import sys
import zipfile

from .conexion import RAIZ

ZIP = RAIZ / "outputs" / "entrega" / "TP2_Trabajo2_Adell_Giannice_Mazzola.zip"
CONTENIDO = {
    "cypher/00_parte_comun.cypher": RAIZ / "src" / "cypher" / "00_parte_comun.cypher",
    "cypher/01_ejercicio1.cypher": RAIZ / "src" / "cypher" / "01_ejercicio1.cypher",
    "cypher/02_ejercicio2.cypher": RAIZ / "src" / "cypher" / "02_ejercicio2.cypher",
    "cypher/03_ejercicio3.cypher": RAIZ / "src" / "cypher" / "03_ejercicio3.cypher",
    "notebook/ej3_4_pairre.ipynb": RAIZ / "src" / "notebooks" / "ej3_4_pairre.ipynb",
    "informe/TP2_Trabajo2_informe.pdf": RAIZ / "outputs" / "informe" / "TP2_Trabajo2_informe.pdf",
}


def notebook_ejecutado(ruta) -> bool:
    nb = json.loads(ruta.read_text(encoding="utf-8"))
    celdas = [c for c in nb["cells"] if c["cell_type"] == "code"]
    sin_error = all(o.get("output_type") != "error" for c in celdas for o in c.get("outputs", []))
    return bool(celdas) and all(c.get("execution_count") for c in celdas) and sin_error


def main() -> int:
    faltan = [str(p.relative_to(RAIZ)) for p in CONTENIDO.values() if not p.exists()]
    if faltan:
        print("Faltan archivos:", *faltan, sep="\n  ", file=sys.stderr)
        return 1
    if not notebook_ejecutado(CONTENIDO["notebook/ej3_4_pairre.ipynb"]):
        print("El notebook no está ejecutado completo (o tiene errores).", file=sys.stderr)
        return 1

    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for nombre, ruta in CONTENIDO.items():
            z.write(ruta, nombre)
    with zipfile.ZipFile(ZIP) as z:
        nombres = z.namelist()
    print(f"{ZIP.relative_to(RAIZ)} ({ZIP.stat().st_size / 1024:.0f} KB)")
    for n in nombres:
        print("  ", n)
    assert sorted(nombres) == sorted(CONTENIDO), "el zip no tiene exactamente el contenido esperado"
    return 0


if __name__ == "__main__":
    sys.exit(main())
