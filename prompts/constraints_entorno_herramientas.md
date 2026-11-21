# Constraints — Entorno y herramientas

- Neo4j Desktop local con **APOC + GDS**, usando la app Query. No se toca el DBMS `grafos-uca`.
- Python en un **env conda nuevo `grafos-tp2`** (Python 3.12, torch CPU, pykeen, neo4j, pandas, ipykernel, nbconvert). No se toca el env `tp2`.
- **Ollama no se usa**: el Trabajo 2 no tiene GraphRAG (el modelo `llama3.2:3b` de las NOTAS es solo para los grupos con GraphRAG).
- Las NOTAS piden no correr Neo4j, PyKEEN y Ollama a la vez, así que PyKEEN puede entrenar con Neo4j apagado.
