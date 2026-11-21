"""Análisis y render de planes de ejecución (EXPLAIN / PROFILE) devueltos por el driver.

El driver entrega el plan como un dict anidado:
    {'operatorType', 'identifiers', 'args', 'children', ['dbHits', 'rows', 'pageCacheHits',
     'pageCacheMisses', 'time']}
Las claves de métricas solo existen en PROFILE.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

Plan = dict[str, Any]


def _args(nodo: Plan) -> dict[str, Any]:
    return nodo.get("args") or nodo.get("arguments") or {}


def recorrer(nodo: Plan, profundidad: int = 0) -> Iterator[tuple[int, Plan]]:
    """Recorre el árbol en preorden (raíz primero, como lo muestra Neo4j)."""
    yield profundidad, nodo
    for hijo in nodo.get("children", []) or []:
        yield from recorrer(hijo, profundidad + 1)


def operador_inicial(plan: Plan) -> str:
    """Hoja más profunda de la rama izquierda: el operador donde empieza la ejecución."""
    nodo = plan
    while nodo.get("children"):
        nodo = nodo["children"][0]
    return limpiar_operador(nodo.get("operatorType", "?"))


def limpiar_operador(nombre: str) -> str:
    # Neo4j agrega el sufijo "@neo4j" (base de datos) a cada operador.
    return nombre.split("@")[0]


def resumen(plan: Plan | None) -> dict[str, Any]:
    if not plan:
        return {}
    raiz = _args(plan)
    nodos = list(recorrer(plan))
    db_hits = sum(int(n.get("dbHits", 0) or 0) for _, n in nodos)
    operadores = [limpiar_operador(n.get("operatorType", "?")) for _, n in nodos]
    eager = [
        {"paso": i + 1, "operador": op, "profundidad": nodos[i][0]}
        for i, op in enumerate(operadores)
        if op.startswith("Eager") and op not in ("EagerAggregation",)
    ]
    return {
        "runtime": raiz.get("runtime"),
        "runtime_impl": raiz.get("runtime-impl"),
        "planner": raiz.get("planner"),
        "version": raiz.get("version") or raiz.get("Version"),
        "operador_inicial": operador_inicial(plan),
        "operadores_preorden": operadores,
        "db_hits_total": db_hits if any("dbHits" in n for _, n in nodos) else None,
        "tiene_eager": bool(eager),
        "eager": eager,
        "nota_eager": (
            "Los pasos se cuentan en preorden desde la raíz (1 = ProduceResults/raíz). "
            "EagerAggregation no es una barrera Eager de lectura/escritura y se excluye."
        ),
    }


def _fmt(n: Any) -> str:
    if n is None or n == "":
        return ""
    if isinstance(n, float):
        return f"{n:,.1f}".replace(",", ".")
    if isinstance(n, int):
        return f"{n:,}".replace(",", ".")
    return str(n)


def tabla_texto(plan: Plan, titulo: str = "") -> str:
    """Tabla del plan al estilo de Neo4j: operador (indentado), detalles y métricas."""
    filas = []
    for prof, nodo in recorrer(plan):
        a = _args(nodo)
        detalles = str(a.get("Details", "")).replace("\n", " ")
        if len(detalles) > 70:
            detalles = detalles[:67] + "..."
        tiempo = nodo.get("time")
        filas.append([
            ("| " * prof) + "+" + limpiar_operador(nodo.get("operatorType", "?")),
            detalles,
            _fmt(round(a["EstimatedRows"], 1) if isinstance(a.get("EstimatedRows"), float) else a.get("EstimatedRows")),
            _fmt(nodo.get("rows")),
            _fmt(nodo.get("dbHits")),
            (f"{_fmt(nodo.get('pageCacheHits'))}/{_fmt(nodo.get('pageCacheMisses'))}"
             if "pageCacheHits" in nodo else ""),
            _fmt(round(tiempo / 1e6, 3)) if isinstance(tiempo, (int, float)) and tiempo else "",
        ])
    encabezado = ["Operador", "Detalles", "Filas est.", "Filas", "DB hits", "Page cache h/m", "Tiempo (ms)"]
    anchos = [max(len(str(x)) for x in col) for col in zip(encabezado, *filas)]

    def linea(valores):
        return "| " + " | ".join(str(v).ljust(w) for v, w in zip(valores, anchos)) + " |"

    sep = "+-" + "-+-".join("-" * w for w in anchos) + "-+"
    r = resumen(plan)
    cabecera = []
    if titulo:
        cabecera.append(titulo)
    cabecera.append(
        f"Runtime: {r.get('runtime')} ({r.get('runtime_impl')}) | Planner: {r.get('planner')} | "
        f"Operador inicial: {r.get('operador_inicial')}"
        + (f" | DB hits totales: {_fmt(r.get('db_hits_total'))}" if r.get("db_hits_total") is not None else "")
        + f" | Eager: {'sí, paso(s) ' + ', '.join(str(e['paso']) for e in r['eager']) if r['tiene_eager'] else 'no'}"
    )
    return "\n".join(cabecera + [sep, linea(encabezado), sep] + [linea(f) for f in filas] + [sep])


def guardar_render(plan: Plan, destino_sin_ext: Path, titulo: str) -> None:
    """Escribe <destino>.txt y <destino>.png con la tabla del plan."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    texto = tabla_texto(plan, titulo)
    destino_sin_ext.parent.mkdir(parents=True, exist_ok=True)
    # Los ids llevan puntos (p. ej. "2.1_profile"): no usar with_suffix, que cortaría en el punto.
    txt = destino_sin_ext.with_name(destino_sin_ext.name + ".txt")
    png = destino_sin_ext.with_name(destino_sin_ext.name + ".png")
    original = _args(plan).get("string-representation")
    contenido = texto
    if original:
        contenido += "\n\n--- Representación original de Neo4j ---\n" + str(original)
    txt.write_text(contenido + "\n", encoding="utf-8")

    lineas = texto.splitlines()
    ancho = max(len(l) for l in lineas)
    fig = plt.figure(figsize=(max(6.0, ancho * 0.062), max(1.2, len(lineas) * 0.19 + 0.3)), dpi=150)
    fig.text(0.01, 0.98, texto, family="monospace", fontsize=7.5, va="top", ha="left")
    fig.savefig(png, bbox_inches="tight", facecolor="white")
    plt.close(fig)
