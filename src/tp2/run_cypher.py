"""Runner de scripts .cypher del TP: ejecuta paso a paso y guarda la evidencia en outputs/.

Formato del .cypher: cada sentencia va precedida por un marcador

    // @paso <id> [medir=N]

y termina en ';'. Lo que haya antes del primer marcador (encabezado) debe ser solo comentarios.
Cada paso se ejecuta en una transacción implícita (autocommit), requisito de
CALL { ... } IN TRANSACTIONS. Con medir=N se hace 1 corrida de calentamiento y N corridas
medidas; se informa la mediana de (result_available_after + result_consumed_after).

Salidas (por script <s> y paso <id>):
    outputs/resultados/<s>/<id>.csv        registros devueltos
    outputs/resultados/<s>/<id>.json       contadores, tiempos, resumen del plan
    outputs/resultados/<s>/_ejecucion.json estado de cada paso
    outputs/planes/<id>.txt|.png            render del plan (si hubo EXPLAIN/PROFILE)

Uso:
    python -m src.tp2.run_cypher src/cypher/01_ejercicio1.cypher [--solo id1,id2]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from neo4j.graph import Node, Path as GPath, Relationship

from .conexion import RAIZ, obtener_driver
from .planes import guardar_render, resumen

MARCADOR = re.compile(r"^\s*//\s*@paso\s+(\S+)(.*)$")


def parsear(texto: str) -> list[dict[str, Any]]:
    pasos: list[dict[str, Any]] = []
    actual: dict[str, Any] | None = None
    encabezado: list[str] = []
    for linea in texto.splitlines():
        m = MARCADOR.match(linea)
        if m:
            if actual:
                pasos.append(actual)
            opciones = dict(re.findall(r"(\w+)=(\S+)", m.group(2)))
            actual = {"id": m.group(1), "opciones": opciones, "lineas": []}
        elif actual is None:
            encabezado.append(linea)
        else:
            actual["lineas"].append(linea)
    if actual:
        pasos.append(actual)

    codigo_suelto = [l for l in encabezado if l.strip() and not l.strip().startswith("//")]
    if codigo_suelto:
        raise ValueError(f"Hay código antes del primer '// @paso': {codigo_suelto[0]!r}")

    ids = set()
    for p in pasos:
        if p["id"] in ids:
            raise ValueError(f"Id de paso repetido: {p['id']}")
        ids.add(p["id"])
        cuerpo = "\n".join(p.pop("lineas"))
        corte = cuerpo.rfind(";")
        if corte == -1:
            raise ValueError(f"El paso {p['id']} no termina en ';'")
        resto = cuerpo[corte + 1 :]
        if any(l.strip() and not l.strip().startswith("//") for l in resto.splitlines()):
            raise ValueError(f"El paso {p['id']} tiene código después del ';' final")
        p["sentencia"] = cuerpo[:corte].strip()
    return pasos


def a_serializable(v: Any) -> Any:
    if isinstance(v, Node):
        return {"_etiquetas": sorted(v.labels), **dict(v.items())}
    if isinstance(v, Relationship):
        return {"_tipo": v.type, **dict(v.items())}
    if isinstance(v, GPath):
        return [a_serializable(n) for n in v.nodes]
    if isinstance(v, (list, tuple)):
        return [a_serializable(x) for x in v]
    if isinstance(v, dict):
        return {k: a_serializable(x) for k, x in v.items()}
    if hasattr(v, "iso_format"):  # tipos temporales de neo4j
        return v.iso_format()
    return v


def celda(v: Any) -> Any:
    v = a_serializable(v)
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return v


def ejecutar_una_vez(session, sentencia: str):
    resultado = session.run(sentencia)
    registros = list(resultado)
    resumen_drv = resultado.consume()
    return registros, resumen_drv


def mostrar(id_paso: str, claves: list[str], registros: list, max_filas: int = 12) -> None:
    if not claves:
        return
    filas = [[str(celda(r[k])) for k in claves] for r in registros[:max_filas]]
    filas = [[c if len(c) <= 60 else c[:57] + "..." for c in f] for f in filas]
    anchos = [max([len(k)] + [len(f[i]) for f in filas]) for i, k in enumerate(claves)]
    print("    " + " | ".join(k.ljust(w) for k, w in zip(claves, anchos)))
    for f in filas:
        print("    " + " | ".join(c.ljust(w) for c, w in zip(f, anchos)))
    if len(registros) > max_filas:
        print(f"    ... ({len(registros)} filas en total)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--solo", default="", help="ids de pasos separados por coma")
    ap.add_argument("--resultados", type=Path, default=RAIZ / "outputs" / "resultados")
    ap.add_argument("--planes", type=Path, default=RAIZ / "outputs" / "planes")
    args = ap.parse_args(argv)

    script = args.script if args.script.is_absolute() else (Path.cwd() / args.script)
    pasos = parsear(script.read_text(encoding="utf-8"))
    solo = {s.strip() for s in args.solo.split(",") if s.strip()}
    if solo:
        desconocidos = solo - {p["id"] for p in pasos}
        if desconocidos:
            print(f"Ids inexistentes: {sorted(desconocidos)}", file=sys.stderr)
            return 2
        pasos = [p for p in pasos if p["id"] in solo]

    carpeta = args.resultados / script.stem
    carpeta.mkdir(parents=True, exist_ok=True)
    if not solo:  # corrida completa: se limpia la evidencia anterior de este script
        for viejo in list(carpeta.glob("*.csv")) + list(carpeta.glob("*.json")):
            viejo.unlink()

    driver, base = obtener_driver()
    bitacora = {"script": str(script.relative_to(RAIZ)) if script.is_relative_to(RAIZ) else str(script),
                "inicio": datetime.now().isoformat(timespec="seconds"), "pasos": []}
    codigo_salida = 0
    try:
        with driver.session(database=base) as session:
            for p in pasos:
                pid, sentencia = p["id"], p["sentencia"]
                medir = int(p["opciones"].get("medir", 0))
                print(f"[{pid}] ...", flush=True)
                t0 = time.perf_counter()
                try:
                    tiempos = []
                    if medir:
                        ejecutar_una_vez(session, sentencia)  # calentamiento (planificación y caché)
                        for _ in range(medir):
                            registros, s = ejecutar_una_vez(session, sentencia)
                            tiempos.append((s.result_available_after or 0) + (s.result_consumed_after or 0))
                    else:
                        registros, s = ejecutar_una_vez(session, sentencia)
                except Exception as exc:
                    msg = f"{type(exc).__name__}: {exc}"
                    print(f"[{pid}] ERROR {msg}", file=sys.stderr)
                    bitacora["pasos"].append({"id": pid, "estado": "error", "error": msg})
                    codigo_salida = 1
                    break
                pared = time.perf_counter() - t0

                claves = list(registros[0].keys()) if registros else list(getattr(s, "keys", None) or [])
                with (carpeta / f"{pid}.csv").open("w", newline="", encoding="utf-8") as fh:
                    w = csv.writer(fh)
                    w.writerow(claves)
                    for r in registros:
                        w.writerow([celda(r[k]) for k in claves])

                plan = s.profile or s.plan
                info = {
                    "id": pid,
                    "sentencia": sentencia,
                    "filas": len(registros),
                    "tipo_consulta": s.query_type,
                    "contadores": {k: v for k, v in vars(s.counters).items() if not k.startswith("_") and v},
                    "result_available_after_ms": s.result_available_after,
                    "result_consumed_after_ms": s.result_consumed_after,
                    "tiempo_pared_s": round(pared, 3),
                    "plan_tipo": "PROFILE" if s.profile else ("EXPLAIN" if s.plan else None),
                    "plan_resumen": resumen(plan) if plan else None,
                    "plan": plan,
                }
                if medir:
                    info["medicion"] = {"repeticiones": medir, "tiempos_ms": tiempos,
                                        "mediana_ms": statistics.median(tiempos),
                                        "criterio": "1 calentamiento + N medidas; available_after + consumed_after"}
                notas = [
                    {"gql_status": o.gql_status, "descripcion": o.status_description,
                     "clasificacion": str(o.classification)}
                    for o in s.gql_status_objects if o.is_notification
                ]
                if notas:
                    info["notificaciones"] = notas
                (carpeta / f"{pid}.json").write_text(
                    json.dumps(info, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
                if plan:
                    guardar_render(plan, args.planes / pid, f"{pid} ({info['plan_tipo']})")

                extra = f" | mediana {info['medicion']['mediana_ms']} ms" if medir else ""
                if plan:
                    r = info["plan_resumen"]
                    extra += (f" | {info['plan_tipo']}: inicial={r['operador_inicial']} "
                              f"dbHits={r['db_hits_total']} runtime={r['runtime']} eager={r['tiene_eager']}")
                print(f"[{pid}] ok: {len(registros)} filas, {pared:.2f} s{extra}")
                mostrar(pid, claves, registros)
                bitacora["pasos"].append({"id": pid, "estado": "ok", "filas": len(registros),
                                          "tiempo_pared_s": round(pared, 3)})
    finally:
        driver.close()
        bitacora["fin"] = datetime.now().isoformat(timespec="seconds")
        bitacora["estado"] = "ok" if codigo_salida == 0 else "error"
        nombre = "_ejecucion.json" if not solo else "_ejecucion_parcial.json"
        (carpeta / nombre).write_text(json.dumps(bitacora, ensure_ascii=False, indent=2), encoding="utf-8")
    return codigo_salida


if __name__ == "__main__":
    sys.exit(main())
