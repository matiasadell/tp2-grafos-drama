# CONSIGNA — Trabajo Práctico 2

**Bases de Datos Orientadas a Grafos** · Segundo Cuatrimestre 2026 · Docente: José Canelón
Fuente: [context/TP_2-2.pdf](context/TP_2-2.pdf)

> El TP abarca las **Unidades V, VI y VII**. Los siete grupos trabajan sobre el mismo grafo de películas (dataset de recomendaciones de Neo4j: MovieLens + OMDb) y cada uno resuelve tres ejercicios según su eje. Este archivo transcribe el **Trabajo 2** más las secciones comunes a todos los grupos.

**Fecha límite de entrega:** 23 de noviembre de 2026, 23:59, en el EVA.

---

## Esquema del grafo (común a todos los grupos)

**Nodos**

| Etiqueta | Propiedades |
|---|---|
| `:Movie` | `title`, `year`, `plot`, `imdbRating` |
| `:Person` | `name` (pueden tener además `:Actor` y/o `:Director`) |
| `:Genre` | `name` |
| `:User` | `name` |

**Relaciones**

| Patrón | Propiedades |
|---|---|
| `(:Person)-[:ACTED_IN]->(:Movie)` | — |
| `(:Person)-[:DIRECTED]->(:Movie)` | — |
| `(:Movie)-[:IN_GENRE]->(:Genre)` | — |
| `(:User)-[:RATED]->(:Movie)` | `rating`, `timestamp` |

Los géneros son los de MovieLens, en inglés (Action, Drama, Comedy, Sci-Fi, Crime, Adventure, Horror, …).

---

## Trabajo 2

- **Grupo:** Matías Adell, Agustín Giannice, Facundo Mazzola
- **Eje asignado:** Drama (género «Drama»)
- **Dataset:** grafo de películas (Neo4j Recommendations)
- **Película ancla:** la película del género «Drama» con más calificaciones `[:RATED]` (desempatar por título). Usar esa misma película donde la consigna la pida.

### Ejercicio 1 — Graph Data Science: proyección y algoritmos

| # | Consigna | Entregable |
|---|---|---|
| 1.1 | Proyectar a memoria un grafo Usuario–Película a partir de `[:RATED]`, **ponderado por rating** (llamarlo **`califW`**). | La proyección, con su `nodeCount` y `relationshipCount`. |
| 1.2 | Calcular la **intermediación (betweenness)** sobre la proyección. | El top 10 del ranking. |
| 1.3 | Detectar comunidades con **propagación de etiquetas (Label Propagation)** sobre la proyección. | La cantidad de comunidades/componentes y el tamaño de las 5 mayores. |
| 1.4 | Calcular la similitud entre pares con **KNN sobre un embedding de los usuarios**. | Los 10 pares más similares (sin autosimilitud), con su puntaje. |
| 1.5 | Correr el algoritmo de centralidad del punto 1.2 (betweenness) en los modos **`stream`**, **`stats`** y **`write`**. | La propiedad que persiste el modo `write` y la captura de cada corrida. |

### Ejercicio 2 — Índices, planes de ejecución y escritura por lotes

| # | Consigna | Entregable |
|---|---|---|
| 2.1 | Con `PROFILE` y **sin** el índice específico, medir una consulta que filtre películas por un **rango de años** (p. ej. 1990–1999). | El operador inicial, los db hits y el tiempo. |
| 2.2 | Crear un **índice de RANGO sobre `Movie.year`** y volver a medir la misma consulta con `PROFILE`. | El nuevo plan (el seek por índice), sus db hits y tiempo, y el factor de mejora. |
| 2.3 | Con `EXPLAIN` mostrar el plan sin ejecutar y, con `PROFILE`, identificar el **runtime** (pipelined o slotted) y señalar un operador **Eager** si aparece. | El runtime informado y, si aparece, en qué paso está el operador Eager. |
| 2.4 | Escritura por lotes, para normalizar las calificaciones: agregar a cada `[:RATED]` la propiedad **`ratingNorm`** (rating menos el promedio de ese usuario), usando `CALL { … } IN TRANSACTIONS`. | La sentencia y la consulta de verificación con su resultado. |

### Ejercicio 3 — Embeddings, ML en GDS y Python

| # | Consigna | Entregable |
|---|---|---|
| 3.1 | Generar un embedding de nodo con **node2vec** sobre la proyección. | El vector de 5 nodos y su dimensión. |
| 3.2 | Definir el objetivo de **predicción de enlaces**: nuevas relaciones `[:RATED]` entre usuarios y películas; acotar según las [Notas](#notas). | La cantidad de nodos y relaciones del subgrafo de entrenamiento. |
| 3.3 | Armar y entrenar un **pipeline de predicción de enlaces** usando el embedding como feature. | El **AUCPR** de test y los 5 pares con mayor probabilidad predicha. |
| 3.4 | En el notebook de Python: **completado de knowledge graph con PairRE**. | Las métricas (**MRR**, **Hits@10**) y 3 hechos propuestos que no estaban en el grafo. |

---

## Parte común: síntesis (todos los grupos)

Sobre el grafo de películas, todos los grupos resuelven además:

1. **Panorama del grafo:** contar nodos por etiqueta y relaciones por tipo (verificar **28.863 nodos** y **166.261 relaciones**) y listar las 3 películas con más calificaciones.
2. **Recomendación base (sin GDS):** para la película ancla, recomendar 10 películas con el patrón
   ```cypher
   (:Movie)<-[:RATED]-(:User)-[:RATED]->(rec:Movie)
   ```
   ordenando por usuarios en común.

---

## Notas

**Entorno.** Neo4j Desktop (local) con APOC y Graph Data Science (GDS), usando la app Query. La parte en Python corre en un notebook en la laptop (CPU, sin GPU): PyKEEN para el completado de KG y Ollama con el modelo liviano `llama3.2:3b` para GraphRAG, sin API key.

**Datos y carga.** El grafo es el dataset de recomendaciones de Neo4j (28.863 nodos y 166.261 relaciones), construido a partir de MovieLens y metadatos de OMDb ([github.com/neo4j-graph-examples/recommendations](https://github.com/neo4j-graph-examples/recommendations)). Se carga restaurando un volcado (dump), **no con `LOAD CSV`**:
1. Descargar `recommendations-50.dump`.
2. Arrastrarlo a la sección **Files** del proyecto en Neo4j Desktop.
3. Elegir **«Create new DBMS from dump»**.

Todos los grupos parten del mismo grafo.

**Factibilidad.**
- Usar embeddings de dimensión moderada (p. ej. **128**).
- En node2vec, parámetros moderados.
- En betweenness, usar **muestreo**.
- Acotar el entrenamiento de ML a las películas con **al menos 20 calificaciones** (o a los 5 géneros más frecuentes).
- Limitar a unas decenas de miles las relaciones creadas por lotes (`SIMILAR_GENERO`, `ACTUO_CON`).
- En Python, correr PyKEEN sobre una **muestra de tripletas estructurales** (`IN_GENRE` y `ACTED_IN`).
- **No ejecutar a la vez** Neo4j, PyKEEN y Ollama.

---

## Indicaciones

- **Reproducibilidad:** fijar la semilla (`randomSeed: 42` en GDS; `seed`/`random_state = 42` en Python) en todo lo que la acepte.
- **Proyecciones:** salvo indicación en contrario, proyectar como no dirigido (`UNDIRECTED`).
- **Nombres:** respetar los nombres de proyección, índices y propiedades que fija cada consigna. Para el Trabajo 2: `califW` y `ratingNorm`.
- **Evidencia:** los planes `PROFILE`/`EXPLAIN` se entregan como captura; los resultados numéricos, como tabla o captura de la salida de Query.
- **Idempotencia:** iniciar cada script liberando lo que crea:
  ```cypher
  CALL gds.graph.drop('…', false);
  CALL gds.pipeline.drop('…', false);
  CALL gds.model.drop('…', false);
  ```

---

## Entrega del trabajo

Cada grupo entrega **un archivo comprimido** con:

- [ ] Los scripts `.cypher` de los tres ejercicios y de la parte común.
- [ ] El notebook de Python **ejecutado**.
- [ ] Un informe en **PDF (máx. 8 páginas)** con el entregable pedido por consigna: capturas de los planes `PROFILE` del Ejercicio 2 y tablas de resultados.

Se sube al **EVA** a más tardar el **23 de noviembre de 2026 a las 23:59**.

---

## Checklist de entregables (Trabajo 2)

- [ ] **Común 1:** conteo de nodos por etiqueta y de relaciones por tipo (28.863 / 166.261) + top 3 películas más calificadas
- [ ] **Común 2:** película ancla de Drama + 10 recomendaciones por usuarios en común
- [ ] **1.1** `califW`: `nodeCount`, `relationshipCount`
- [ ] **1.2** Betweenness: top 10
- [ ] **1.3** Label Propagation: n.º de comunidades + tamaño de las 5 mayores
- [ ] **1.4** KNN sobre embedding de usuarios: top 10 pares + puntaje
- [ ] **1.5** Betweenness en `stream` / `stats` / `write`: propiedad escrita + capturas
- [ ] **2.1** `PROFILE` sin índice (rango de años): operador inicial, db hits, tiempo
- [ ] **2.2** Índice de RANGO sobre `Movie.year`: nuevo plan, db hits, tiempo, factor de mejora
- [ ] **2.3** `EXPLAIN` + `PROFILE`: runtime y operador Eager (si aparece)
- [ ] **2.4** `ratingNorm` con `CALL { … } IN TRANSACTIONS`: sentencia + verificación
- [ ] **3.1** node2vec: vector de 5 nodos + dimensión
- [ ] **3.2** Subgrafo de entrenamiento para link prediction: n.º de nodos y relaciones
- [ ] **3.3** Pipeline de link prediction: AUCPR de test + top 5 pares predichos
- [ ] **3.4** PairRE (PyKEEN): MRR, Hits@10 + 3 hechos nuevos propuestos
