# Constraints — Reglas de la cátedra

- **Indicaciones:**
  - `randomSeed: 42` en GDS y `seed`/`random_state` 42 en Python, en todo lo que lo acepte.
  - Proyecciones UNDIRECTED salvo indicación en contrario.
  - Respetar los nombres que fija la consigna (`califW`, `ratingNorm`).
  - PROFILE/EXPLAIN como captura; los resultados numéricos como tabla o captura de Query.
  - Cada script empieza con `gds.graph.drop(…, false)`, `gds.pipeline.drop(…, false)` y `gds.model.drop(…, false)`.
- **Factibilidad:**
  - Embeddings de dimensión 128.
  - node2vec con parámetros moderados.
  - Betweenness con muestreo.
  - ML acotado a películas con ≥20 calificaciones.
  - PyKEEN sobre una muestra de tripletas estructurales (`IN_GENRE`, `ACTED_IN`).
