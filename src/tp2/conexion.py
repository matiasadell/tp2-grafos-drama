"""Conexión a Neo4j a partir de las credenciales del archivo .env de la raíz.

Variables reconocidas (en .env o en el entorno):
    NEO4J_URI       por defecto neo4j://127.0.0.1:7687
    NEO4J_USER      por defecto neo4j
    NEO4J_PASSWORD  obligatoria
    NEO4J_DATABASE  por defecto neo4j

Nunca imprime ni devuelve la contraseña en texto.
"""
from __future__ import annotations

import os
from pathlib import Path

from neo4j import Driver, GraphDatabase

RAIZ = Path(__file__).resolve().parents[2]


def _leer_env(ruta: Path = RAIZ / ".env") -> dict[str, str]:
    """Parser mínimo de .env (clave=valor, ignora comentarios y comillas)."""
    valores: dict[str, str] = {}
    if not ruta.exists():
        return valores
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def configuracion() -> dict[str, str]:
    env = _leer_env()

    def valor(clave: str, defecto: str | None = None) -> str | None:
        return os.environ.get(clave) or env.get(clave) or defecto

    password = valor("NEO4J_PASSWORD")
    if not password:
        raise RuntimeError("Falta NEO4J_PASSWORD en .env (en la raíz del proyecto).")
    return {
        "uri": valor("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        "user": valor("NEO4J_USER", "neo4j"),
        "password": password,
        "database": valor("NEO4J_DATABASE", "neo4j"),
    }


def obtener_driver() -> tuple[Driver, str]:
    """Devuelve (driver, nombre_de_base) con la conectividad ya verificada."""
    cfg = configuracion()
    driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
    try:
        driver.verify_connectivity()
    except Exception as exc:  # mensaje claro sin exponer credenciales
        driver.close()
        raise RuntimeError(
            f"No se pudo conectar a {cfg['uri']}. ¿Está iniciado el DBMS "
            f"'tp2-recommendations' en Neo4j Desktop? ({type(exc).__name__})"
        ) from None
    return driver, cfg["database"]
