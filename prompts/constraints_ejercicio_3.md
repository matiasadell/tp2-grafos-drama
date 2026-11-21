# Constraints — Ejercicio 3

Embeddings, predicción de enlaces y PairRE.

- **3.1** node2vec **ponderado** (dim 128, parámetros moderados, seed 42) sobre la proyección. Entregable: el vector de 5 nodos y su dimensión.
- **3.2** Objetivo: nuevas `[:RATED]` usuario–película, acotado a las películas con ≥20 calificaciones. Entregable: nodos y relaciones del subgrafo de entrenamiento.
- **3.3** Pipeline de link prediction con node2vec como **paso del pipeline (`addNodeProperty`)**, para que no haya fuga de datos. Modelos: **regresión logística + Random Forest**, 2–3 configuraciones de cada uno, métrica AUCPR, seed 42. Entregable: AUCPR de test y los 5 pares con mayor probabilidad predicha.
- **3.4** Notebook con **PairRE (PyKEEN)**:
  - Tripletas: todas las `IN_GENRE` y `ACTED_IN` de las películas con ≥20 calificaciones, split 80/10/10 con seed 42.
  - Se obtienen con el driver `neo4j` y se cachean en `outputs/kg/triples.tsv`; si el TSV ya existe, el notebook no se conecta a Neo4j.
  - Entregable: MRR y Hits@10, y 3 hechos nuevos: las predicciones de mayor score para `(película, IN_GENRE, Drama)` entre películas que hoy no son Drama.
