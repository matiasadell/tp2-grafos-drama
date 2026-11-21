# Estado — Setup de Neo4j y relevamiento del esquema (Task 2)

Fecha: 2026-11-21.

## Setup realizado

| Ítem | Estado |
|---|---|
| Dump | `recommendations-50.dump` (9,5 MB), descargado de `github.com/neo4j-graph-examples/recommendations` (`data/recommendations-50.dump`) en `C:\Users\matia\Downloads\neo4j-recommendations-dump\`. Hay una copia en `context/`, ignorada por git. |
| DBMS | `tp2-recommendations`, creado por el grupo en Neo4j Desktop 2.2.1 con *Create instance* desde el dump. Neo4j **2026.09.0 Enterprise**. |
| Ruta | `C:\Users\matia\.Neo4jDesktop2\Data\dbmss\dbms-cddf7c97-e694-49c1-93be-5a737fb31239` |
| URI | `neo4j://127.0.0.1:7687`, usuario `neo4j`, contraseña en `.env` |
| Plugins | `apoc-2026.09.0-core.jar`, `neo4j-graph-data-science-2026.09.0.jar`. `dbms.security.procedures.unrestricted=apoc.*,gds.*` |
| Memoria | `server.memory.heap.initial_size=2G`, `heap.max_size=4G`, `pagecache.size=1G`. El original (512m / 1G / 512m) quedó en `conf/neo4j.conf.bak-antes-tp2`. |
| Conexión | Verificada: `gds.version()` = 2026.09.0, `apoc.version()` = 2026.09.0, bases `neo4j` y `system` online. |
| Otro DBMS | `grafos-uca` (2026.09.0), sin tocar. |

## Relevamiento del esquema real

**Totales:** 28.863 nodos y 166.261 relaciones, como dice la consigna.

**Nodos por combinación de etiquetas:**

| Etiquetas | Nodos |
|---|---|
| Actor, Person | 14.956 |
| Movie | 9.125 |
| Director, Person | 3.604 |
| User | 671 |
| Actor, Director, Person | 487 |
| Genre | 20 |

**Índices y constraints que trae el dump:**
- Constraints de unicidad sobre `User.userId`, `Movie.movieId`, `Movie.tmdbId`, `Person.tmdbId` y `Genre.name`.
- Índices RANGE sobre `Movie.tagline`, `Movie.released`, `Person.name`, `Movie.imdbRating`, `User.name`, `Movie.title`, **`Movie.year` (`index_fc5f831e`)** y `Movie.imdbId`.
- El índice LOOKUP de etiquetas.
- ⚠️ **Impacto en el Ej. 2:** el dump ya tiene un índice RANGE sobre `Movie(year)`. Para medir el 2.1 "sin el índice específico", `02_ejercicio2.cypher` tiene que borrar `index_fc5f831e` (y el nuestro, `movie_year_range`) antes de la línea base.

**Tipos:** `Movie.year` es INTEGER en 9.096 películas y NULL en 29, así que el filtro por rango funciona sin conversión.

**Película ancla (Drama, más `[:RATED]`, desempate por título):**

| Título | Año | Calificaciones |
|---|---|---|
| **Forrest Gump** | 1994 | **341** |
| Pulp Fiction | 1994 | 324 |
| Shawshank Redemption, The | 1994 | 311 |

**Corte de ML:** 1.303 películas tienen ≥20 calificaciones.

**Duplicados:** 210 títulos de `Movie` y 32 nombres de `Person` se repiten. En PyKEEN, los IDs de entidad tienen que desambiguarse con `[movieId]` o `[tmdbId]`.

**Procedimientos GDS 2026.09:**
- La predicción de enlaces sigue en beta: `gds.beta.pipeline.linkPrediction.create`, `.addNodeProperty`, `.train` y `.predict.stream`.
- Están disponibles `gds.betweenness.*`, `gds.labelPropagation.*`, `gds.fastRP.*`, `gds.knn.*` y `gds.node2vec.*` (`stream`, `stats`, `mutate`, `write`), excepto `gds.node2vec.stats`.
