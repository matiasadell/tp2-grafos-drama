# Plan: TP2 Grafos — Trabajo 2 (eje Drama)

## Problem & goal

El grupo del Trabajo 2 (Adell, Giannice, Mazzola) tiene que resolver el TP 2 de *Bases de Datos Orientadas a Grafos* (UCA, 2C 2026) sobre el grafo de recomendaciones de Neo4j (MovieLens + OMDb):

- la parte común;
- los Ejercicios 1 (GDS), 2 (índices, planes y lotes) y 3 (embeddings, link prediction y PairRE), en el eje **Drama**.

El proyecto está **terminado** cuando existe `outputs/entrega/TP2_Trabajo2_Adell_Giannice_Mazzola.zip` con:

- los 4 `.cypher`, que corren dos veces seguidas sin errores;
- el notebook PairRE ejecutado;
- un informe PDF de 8 páginas o menos que cubre todos los entregables, con las capturas de Query que saca el grupo.

Todo tiene que estar listo el 22/11/2026 a la noche. La entrega en el EVA cierra el 23/11/2026 a las 23:59.

## Key decisions

- **DBMS:** `tp2-recommendations` (Neo4j 2026.09.0 Enterprise, GDS 2026.09.0, APOC 2026.09.0), en `neo4j://127.0.0.1:7687`. Memoria: heap de 2G a 4G y page cache de 1G. Credenciales en `.env`.
- **Película ancla:** *Forrest Gump* (1994), la de Drama con más calificaciones (341). La consulta la recalcula siempre; nunca va hardcodeada.
- **El dump ya trae `index_fc5f831e`** (RANGE sobre `Movie(year)`). El 2.1 lo borra para medir sin el índice específico y el 2.2 crea el nuestro, `movie_year_range`.
- **Un `.cypher` por bloque de entrega:** `src/cypher/00_parte_comun.cypher`, `01_ejercicio1.cypher`, `02_ejercicio2.cypher` y `03_ejercicio3.cypher`.
  - Cada script es autosuficiente e idempotente: arranca con `gds.*.drop(…, false)` de lo que crea y vuelve a proyectar lo que usa.
  - Se pueden pegar enteros en Query.
- **Marcadores para el runner:** cada sentencia va precedida por `// @paso <id> [medir=N]`.
  - `src/tp2/run_cypher.py` separa el archivo por esos marcadores y ejecuta cada paso en autocommit, que es lo que exige `CALL … IN TRANSACTIONS`.
  - Guarda `outputs/resultados/<script>/<id>.csv` más `<id>.json` (resumen, contadores, tiempos y plan si hay PROFILE/EXPLAIN).
  - Si el paso es PROFILE o EXPLAIN, guarda además un render en `outputs/planes/<id>.png` y `.txt`.
- **Medición de tiempos (Ej. 2):** una corrida de calentamiento y 20 medidas; se informa la mediana de `result_available_after + result_consumed_after` (ms) y la mediana del tiempo de operadores del PROFILE, que es más fino. Los db hits salen del PROFILE, que son deterministas.
- **Parámetros GDS:**

  | Algoritmo | Parámetros |
  |---|---|
  | Betweenness | `samplingSize: 1000`, `samplingSeed: 42`, sin peso |
  | Label Propagation | `relationshipWeightProperty: 'rating'`, `concurrency: 1` |
  | FastRP | `embeddingDimension: 128`, `randomSeed: 42`, `relationshipWeightProperty: 'rating'` |
  | KNN | `nodeLabels: ['User']`, `topK: 10`, `randomSeed: 42`, `concurrency: 1`, `sampleRate: 1.0`, `deltaThreshold: 0.0` |
  | node2vec | `embeddingDimension: 128`, `walkLength: 40`, `walksPerNode: 10`, `iterations: 1`, `relationshipWeightProperty: 'rating'`, `randomSeed: 42`, `concurrency: 1` |

- **Link prediction:**
  - Subgrafo `califLP`, una proyección Cypher de `(:User)-[:RATED]->(:Movie)` restringida a las películas con ≥20 calificaciones, UNDIRECTED y con peso `rating`.
  - Pipeline `pipeLP_drama`, con los procedimientos `gds.beta.pipeline.linkPrediction.*`.
  - node2vec como `addNodeProperty` y feature `hadamard`.
  - Split: `testFraction: 0.1`, `trainFraction: 0.1`, `validationFolds: 3`, `negativeSamplingRatio: 1.0`.
  - Modelos: LR con `penalty` ∈ {0.0, 0.01, 0.1} y RF con {10 árboles, maxDepth 10} y {25 árboles, maxDepth 15}.
  - Entrenamiento con `sourceNodeLabel: 'User'`, `targetNodeLabel: 'Movie'`, `metrics: ['AUCPR']` y `randomSeed: 42`. El modelo se llama `modeloLP_drama`.
- **Python:** env conda `grafos-tp2` (Python 3.12, torch CPU, pykeen, neo4j, pandas, matplotlib, ipykernel, nbconvert, python-dotenv). La especificación queda en `environment.yml`.
- **PairRE:**
  - IDs únicos de entidad: `Título (año)`, con `[movieId]` solo si se repite, y `Nombre`, con `[tmdbId]` solo si se repite. Hay 210 títulos y 32 nombres duplicados.
  - Configuración: `embedding_dim=128`, `num_epochs=100`, `random_seed=42`, split 80/10/10 con `random_state=42`.
- **Informe:** `docs/informe/informe.md` es una plantilla con marcadores (`{{tabla:...}}`, `{{plan:...}}`).
  - `src/tp2/build_informe.py` reemplaza cada marcador por las tablas de `outputs/resultados/`.
  - Para cada imagen usa la captura del grupo si existe en `outputs/capturas/`; si no, el render de `outputs/planes/`.
  - Compila con pandoc + xelatex a `outputs/informe/TP2_Trabajo2_informe.pdf`.

# Phase 1 — Preparación del entorno

## Task 1 — Reorganizar el skill e inicializar git
**Prompts:** constraints_proceso_repositorio.md
**Context:** none
**Objective:** Dejar la raíz limpia (skill en `.claude/skills/project_planner/`) y el proyecto bajo git local.
**Description:**
- Mover `SKILL.md`, `references/`, `assets/`, `scripts/` y `evals/` a `.claude/skills/project_planner/`.
- Crear `.gitignore` con:
  - `.env`, `__pycache__/`, `.ipynb_checkpoints/`;
  - `outputs/kg/modelo/` (checkpoints de PyKEEN);
  - `outputs/entrega/*.zip`, `outputs/informe/*.pdf`, `*.bak*`;
  - `QUESTIONS.md` y `PROMPT.md`, que son temporales.
- Correr `git init`. Antes de commitear, verificar que `git config user.name` y `user.email` existan. Si faltan, pedírselos al usuario; no inventarlos ni tocar la config global.
- Hacer el primer commit con lo que ya existe (CONSIGNA.md, PLAN.md, CLAUDE.md, prompts/, context/, skill movido).
**Outputs:**
- `.claude/skills/project_planner/` — creado (contenido movido desde la raíz)
- `SKILL.md`, `references/`, `assets/`, `scripts/`, `evals/` en la raíz — borrados (movidos)
- `.gitignore` — creado
- `.git/` — creado
**Definition of done:** `git status` está limpio después del primer commit. `git check-ignore .env` devuelve `.env`. En la raíz ya no hay `SKILL.md` y `.claude/skills/project_planner/SKILL.md` existe.

## Task 2 — Dejar asentado el setup de Neo4j y relevar el esquema real
**Prompts:** constraints_setup_neo4j.md, context_entorno_verificado.md, context_consigna.md
**Context:** none
**Objective:** Registrar el setup ya hecho (dump, DBMS, plugins, memoria, `.env`) y los datos del esquema real que condicionan los scripts.
**Description:**
- **Ya hecho en la sesión de planificación:**
  - dump descargado en `C:\Users\matia\Downloads\neo4j-recommendations-dump\`;
  - DBMS `tp2-recommendations` creado por el grupo, con APOC y GDS;
  - `neo4j.conf` con heap de 2G a 4G y page cache de 1G (backup en `neo4j.conf.bak-antes-tp2`);
  - conexión verificada: 28.863 nodos y 166.261 relaciones.
- **Relevamiento:** índices y constraints (en especial `index_fc5f831e` sobre `Movie(year)`), tipo de `Movie.year` (INTEGER, con 29 nulos), película ancla (Forrest Gump, 341), películas con ≥20 calificaciones (1.303), títulos y nombres duplicados (210 y 32) y nombres de procedimientos GDS (LP en `gds.beta.pipeline.linkPrediction.*`).
- Volcar todo eso a una nota de estado.
**Outputs:**
- `docs/estado/setup_neo4j.md` — creado (setup, versiones, ruta del DBMS y relevamiento)
**Definition of done:** La nota menciona el DBMS, las versiones, la memoria, el índice preexistente sobre `year`, la ancla y los nombres de los procedimientos LP. Una consulta de control vuelve a dar 28.863 / 166.261.

## Task 3 — Crear el entorno Python `grafos-tp2`
**Prompts:** constraints_entorno_herramientas.md, constraints_reglas_catedra.md
**Context:** context/Unidad VII/Unidad_VII_Practica_Python.ipynb
**Objective:** Tener un env conda aislado con todo lo necesario para el runner, el notebook y el informe.
**Description:**
- Instalación:
  - `conda create -n grafos-tp2 python=3.12`;
  - torch CPU con `pip install torch --index-url https://download.pytorch.org/whl/cpu`;
  - `pip install pykeen neo4j pandas matplotlib ipykernel nbconvert python-dotenv tabulate`.
- Registrar el kernel con `python -m ipykernel install --user --name grafos-tp2 --display-name "Python (grafos-tp2)"`.
- Exportar `environment.yml` (dependencias declaradas, no un freeze completo).
- No tocar el env `tp2`.
- Si PyKEEN no instala en 3.12, bajar a `python=3.11` y anotarlo.
**Outputs:**
- `D:\miniconda\envs\grafos-tp2\` — creado (fuera del repo)
- `environment.yml` — creado
**Definition of done:** `conda run -n grafos-tp2 python -c "import pykeen, neo4j, torch; print(pykeen.get_version(), torch.cuda.is_available())"` imprime la versión y `False`. `jupyter kernelspec list` muestra `grafos-tp2`.

## Task 4 — Runner de Cypher, conexión y render de planes
**Prompts:** constraints_setup_neo4j.md, constraints_evidencia_capturas.md, constraints_reglas_catedra.md
**Context:** context/Unidad VI/Unidad_VI_Práctica.pdf
**Objective:** Poder ejecutar cualquier `.cypher` del proyecto paso a paso y guardar cada resultado como evidencia en `outputs/`.
**Description:**
- **`src/tp2/conexion.py`:** lee `.env` (`NEO4J_URI`, por defecto `neo4j://127.0.0.1:7687`; `NEO4J_USER`, por defecto `neo4j`; `NEO4J_PASSWORD`) y devuelve el driver. No imprime nunca la contraseña.
- **`src/tp2/run_cypher.py <archivo.cypher> [--solo id1,id2]`:**
  - separa el archivo por los marcadores `// @paso <id> [medir=N]`; el texto de cada paso es una sentencia, sin el `;` final;
  - ejecuta cada paso con `session.run`, en autocommit;
  - guarda los registros en CSV (listas y vectores como JSON) y un `.json` con contadores, `result_available_after`, `result_consumed_after`, `plan`/`profile` y, si hay `medir=N`, los N tiempos con la mediana;
  - si hay plan, genera `.txt` (árbol de operadores con filas, db hits, page cache y `runtime`) y `.png` (el mismo texto con matplotlib, en monoespaciada);
  - escribe `outputs/resultados/<script>/_ejecucion.json` (inicio, fin y estado por paso) y sale con un código distinto de 0 si algún paso falla.
- **`src/tp2/planes.py`:** funciones compartidas de render y para detectar `Eager` y el runtime en el árbol del plan.
- Probar con un `.cypher` mínimo de humo en `outputs/` (no se entrega).
**Outputs:**
- `src/tp2/__init__.py`, `src/tp2/conexion.py`, `src/tp2/run_cypher.py`, `src/tp2/planes.py` — creados
- `outputs/resultados/_humo/` — creado (CSV, JSON y render de un `PROFILE` de prueba)
**Definition of done:** `conda run -n grafos-tp2 python -m src.tp2.run_cypher outputs/_humo.cypher` termina con código 0. Genera el CSV de `MATCH (n) RETURN count(n)` (28863) y el `.png` y `.txt` de un PROFILE. El `.txt` muestra el runtime.

# Phase 2 — Scripts Cypher

## Task 5 — Parte común
**Prompts:** constraints_parte_comun.md, context_consigna.md, constraints_reglas_catedra.md
**Context:** none
**Objective:** Escribir y ejecutar `00_parte_comun.cypher`: panorama, ancla y recomendación base.
**Description:**
- **Pasos:**
  - `C.1_nodos_por_etiqueta`: `labels` y `count`; cuando un nodo tiene varias etiquetas, cuenta por etiqueta individual (`UNWIND labels(n)`) y también por combinación.
  - `C.2_relaciones_por_tipo`.
  - `C.3_totales`: verifica 28.863 y 166.261.
  - `C.4_top3_mas_calificadas`.
  - `C.5_pelicula_ancla`: Drama, más `RATED`, desempate por título.
  - `C.6_recomendacion_base`: patrón `(:Movie)<-[:RATED]-(:User)-[:RATED]->(rec:Movie)` desde la ancla, `rec <> ancla`, `count(DISTINCT u)` como usuarios en común, `ORDER BY usuariosEnComun DESC, rec.title`, `LIMIT 10`.
- La ancla se calcula dentro de cada consulta que la usa (subconsulta `CALL`), no se hardcodea.
**Outputs:**
- `src/cypher/00_parte_comun.cypher` — creado
- `outputs/resultados/00_parte_comun/*.csv|*.json` — creados
**Definition of done:** El runner termina con código 0. `C.3` da 28863 / 166261. `C.5` da *Forrest Gump*. `C.6` tiene 10 filas ordenadas.

## Task 6 — Ejercicio 1 (GDS sobre `califW`)
**Prompts:** constraints_ejercicio_1.md, constraints_reglas_catedra.md, constraints_evidencia_capturas.md
**Context:** context/Unidad V/Unidad_V.pdf, context/Unidad V/Unidad_V_Prácticas.pdf
**Objective:** Escribir y ejecutar `01_ejercicio1.cypher` con los entregables 1.1–1.5.
**Description:**
- **Limpieza:** `gds.graph.drop('califW', false)`, `MATCH (n) WHERE n.betweenness IS NOT NULL REMOVE n.betweenness`, para que el `write` sea reproducible.
- **1.1** `gds.graph.project('califW', ['User','Movie'], {RATED: {orientation: 'UNDIRECTED', properties: 'rating'}})`, que devuelve `nodeCount` y `relationshipCount`. Hay que aclarar que el conteo UNDIRECTED duplica las relaciones.
- **1.2** `gds.betweenness.stream` con muestreo y sin peso: top 10 con etiqueta y nombre (`name` del User o `title` de la Movie).
- **1.3** `gds.labelPropagation.stats` (`communityCount`) y `stream` agregado (tamaño de las 5 mayores), ponderado y con `concurrency: 1`.
- **1.4** `gds.fastRP.mutate` (`mutateProperty: 'embFastRP'`) y luego `gds.knn.stream` sobre `:User`, deduplicando pares con `id(a) < id(b)` (o con `elementId` comparado) y quedándose con el top 10 por `similarity`.
- **1.5** `gds.betweenness.stream` (top 10), `.stats` (`centralityDistribution`, `computeMillis`) y `.write` (`writeProperty: 'betweenness'`, `nodePropertiesWritten`), todos con los mismos parámetros que el 1.2, más una consulta de verificación de la propiedad escrita.
**Outputs:**
- `src/cypher/01_ejercicio1.cypher` — creado
- `outputs/resultados/01_ejercicio1/*.csv|*.json` — creados
**Definition of done:** El runner termina con código 0. `1.1` da `nodeCount` 9796 (671 + 9125). `1.2` y `1.5-stream` coinciden. `1.4` tiene 10 pares distintos y sin autosimilitud. La verificación de `1.5` muestra `betweenness` en `nodePropertiesWritten` nodos.

## Task 7 — Ejercicio 2 (índices, planes y lotes)
**Prompts:** constraints_ejercicio_2.md, constraints_reglas_catedra.md, constraints_evidencia_capturas.md
**Context:** context/Unidad VI/Unidad_VI.pdf, context/Unidad VI/Unidad_VI_Práctica.pdf
**Objective:** Escribir y ejecutar `02_ejercicio2.cypher` con los entregables 2.1–2.4, incluidas las mediciones y los renders de los planes.
**Description:**
- **Preparación:** `DROP INDEX index_fc5f831e IF EXISTS`, `DROP INDEX movie_year_range IF EXISTS` y `SHOW INDEXES` de control (no debe quedar ningún índice sobre `Movie(year)`).
- **2.1** `PROFILE MATCH (m:Movie) WHERE m.year >= 1990 AND m.year <= 1999 RETURN count(m) AS peliculas` con `medir=20`. El operador inicial esperado es `NodeByLabelScan`.
- **2.2**
  - `CREATE INDEX movie_year_range IF NOT EXISTS FOR (m:Movie) ON (m.year)`;
  - `CALL db.awaitIndexes()`;
  - el mismo PROFILE con `medir=20`, donde se espera `NodeIndexSeekByRange`;
  - el factor de mejora (db hits y tiempo), que lo calcula el informe a partir de los dos JSON.
- **2.3**
  - `EXPLAIN` y `PROFILE` de la consulta de rango: runtime desde los argumentos del plan, sin Eager;
  - `EXPLAIN` de la sentencia del 2.4: buscar `Eager` y anotar en qué paso del plan aparece, o que no aparece.
- **2.4** Escribir `ratingNorm` por lotes y verificar:
  ```cypher
  MATCH (u:User)
  CALL (u) {
    MATCH (u)-[r:RATED]->()
    WITH collect(r) AS rs, avg(r.rating) AS prom
    UNWIND rs AS r
    SET r.ratingNorm = r.rating - prom
  } IN TRANSACTIONS OF 50 ROWS
  ```
  La verificación cuenta `RATED` con `ratingNorm` (100.004), muestra el promedio de `ratingNorm` por usuario (≈0) para 5 usuarios y algunas filas de ejemplo con `rating`, `promedio` y `ratingNorm`.
- Si `PROFILE` no admite la sentencia con `IN TRANSACTIONS`, se usa `EXPLAIN` y se documenta.
**Outputs:**
- `src/cypher/02_ejercicio2.cypher` — creado
- `outputs/resultados/02_ejercicio2/*.csv|*.json` — creados
- `outputs/planes/2.1_*.png|txt`, `2.2_*`, `2.3_*` — creados
**Definition of done:** El runner termina con código 0. El plan de `2.1` empieza con un scan, sin índice; el de `2.2` usa `NodeIndexSeekByRange` sobre `movie_year_range`, con menos db hits. El runtime queda informado. `2.4` da 100.004 relaciones con `ratingNorm` y promedio ≈0 por usuario.

## Task 8 — Ejercicio 3 en GDS (node2vec y link prediction)
**Prompts:** constraints_ejercicio_3.md, constraints_reglas_catedra.md
**Context:** context/Unidad VII/Unidad_VII_Practica_Neo4j_GDS.pdf, context/Unidad VII/Unidad_VII_Guia de la Practica.pdf
**Objective:** Escribir y ejecutar `03_ejercicio3.cypher` con los entregables 3.1–3.3.
**Description:**
- **Limpieza:** `gds.graph.drop('califW', false)`, `gds.graph.drop('califLP', false)`, `gds.pipeline.drop('pipeLP_drama', false)`, `gds.model.drop('modeloLP_drama', false)`, y se vuelve a proyectar `califW` igual que en el 1.1.
- **3.1** `gds.node2vec.stream` con los parámetros de las decisiones clave, para 5 nodos elegidos de forma determinista: la ancla, la segunda película con más calificaciones y los 3 usuarios con más calificaciones. Devuelve `size(embedding)` (128) y el vector completo; el CSV guarda los 128 valores.
- **3.2** Proyección Cypher `califLP`:
  ```cypher
  MATCH (u:User)-[r:RATED]->(m:Movie)
  WHERE COUNT { (m)<-[:RATED]-() } >= 20
  WITH gds.graph.project('califLP', u, m,
    {sourceNodeLabels: 'User', targetNodeLabels: 'Movie',
     relationshipType: 'RATED', relationshipProperties: {rating: r.rating}},
    {undirectedRelationshipTypes: ['RATED']}) AS g
  RETURN g.nodeCount, g.relationshipCount
  ```
  Además, un conteo Cypher de las `RATED` de la base que entran en el subgrafo.
- **3.3**
  - Construir el pipeline: `create`, `addNodeProperty` de node2vec con `mutateProperty: 'emb'`, `addFeature('hadamard', {nodeProperties: ['emb']})`, `configureSplit`, 3 `addLogisticRegression` y 2 `addRandomForest`.
  - Entrenar: `train` sobre `califLP`, que devuelve `modelInfo.bestParameters`, `modelInfo.metrics.AUCPR` (train, validation, outerTrain y **test**) y `modelSelectionStats`.
  - Predecir: `predict.stream` con `topN: 5`, mostrando el usuario, la película y la probabilidad.
- Si el entrenamiento pasa de ~10 minutos, bajar `walksPerNode` a 5 dentro del pipeline y anotarlo en la nota de la tarea.
**Outputs:**
- `src/cypher/03_ejercicio3.cypher` — creado
- `outputs/resultados/03_ejercicio3/*.csv|*.json` — creados
**Definition of done:** El runner termina con código 0. `3.1` muestra 5 vectores de dimensión 128. `3.2` informa `nodeCount` y `relationshipCount`. `3.3` informa el AUCPR de test (> 0,5), el modelo ganador y 5 pares usuario→película que no existen en la base (se verifica con `NOT EXISTS`).

# Phase 3 — Notebook PairRE

## Task 9 — Notebook 3.4: completado de KG con PairRE
**Prompts:** constraints_ejercicio_3.md, constraints_entorno_herramientas.md, constraints_reglas_catedra.md
**Context:** context/Unidad VII/Unidad_VII_Practica_Python.ipynb, context/Unidad VII/Unidad_VII_Guia de la Practica.pdf
**Objective:** Crear y ejecutar `src/notebooks/ej3_4_pairre.ipynb` con MRR, Hits@10 y 3 hechos nuevos `(película, IN_GENRE, Drama)`.
**Description:**
- **Secciones del notebook** (markdown en español, estilo de la cátedra):
  - **0. Entorno y semillas:** seed 42 en `random`, `numpy` y `torch`; la línea de pip comentada.
  - **1. Tripletas:**
    - si `outputs/kg/triples.tsv` existe, se lee;
    - si no, se consulta Neo4j con el driver (`src.tp2.conexion`): `IN_GENRE` y `ACTED_IN` de las películas con ≥20 calificaciones, con los IDs únicos de entidad de las decisiones clave;
    - se guarda el TSV y se muestran los conteos por relación.
  - **2. Split:** `TriplesFactory.from_labeled_triples` y `split([0.8, 0.1, 0.1], random_state=42)`.
  - **3. Entrenamiento:** `pipeline(model='PairRE', embedding_dim=128, num_epochs=100, random_seed=42)` y la curva de pérdida.
  - **4. Métricas:** MRR y Hits@10 (*both / realistic*), guardadas en `outputs/kg/pairre_metricas.json`.
  - **5. Hechos nuevos:**
    - `predict_target(model, relation='IN_GENRE', tail='Drama', triples_factory=...)`;
    - filtrar a entidades película;
    - excluir las que ya son Drama, sea en el TSV o en train, validación o test;
    - quedarse con el top 3 y guardarlo en `outputs/kg/hechos_propuestos.csv`, con un comentario sobre si son plausibles.
- **Ejecución:** obtener el TSV con Neo4j encendido, apagar Neo4j durante el entrenamiento según las NOTAS (opcional, porque el notebook ya lee del caché) y correr `jupyter nbconvert --to notebook --execute --inplace` con el kernel `grafos-tp2`.
**Outputs:**
- `src/notebooks/ej3_4_pairre.ipynb` — creado y ejecutado (con las salidas guardadas)
- `outputs/kg/triples.tsv`, `outputs/kg/pairre_metricas.json`, `outputs/kg/hechos_propuestos.csv` — creados
**Definition of done:** El notebook ejecutado no tiene celdas con error. El JSON tiene `mrr` y `hits_at_10`. El CSV tiene 3 películas que hoy no están en Drama según la base, cosa que se verifica con una consulta.

# Phase 4 — Evidencia, verificación, informe y entrega

## Task 10 — Checklist de capturas para el grupo
**Prompts:** constraints_evidencia_capturas.md, constraints_ejercicio_1.md, constraints_ejercicio_2.md
**Context:** none
**Objective:** Dejarle al grupo una guía exacta de qué correr en Query y con qué nombre guardar cada captura.
**Description:**
- **Orden de pasos en Query** (importa el estado del índice):
  1. preparación (borrar índices);
  2. 2.1 PROFILE sin índice;
  3. 2.2 crear el índice y repetir el PROFILE;
  4. 2.3 EXPLAIN de la consulta de rango;
  5. 2.3 EXPLAIN de la escritura;
  6. 1.5 las corridas `stream`, `stats` y `write` (antes hay que proyectar `califW`).
- Para cada paso: la consulta lista para copiar, qué tiene que verse en la captura (el plan expandido, el runtime, los db hits) y el nombre del archivo (por ejemplo, `outputs/capturas/2.1_profile_sin_indice.png`).
- Agregar `outputs/capturas/README.md` con la lista de nombres esperados.
**Outputs:**
- `docs/checklist_capturas.md` — creado
- `outputs/capturas/README.md` — creado
**Definition of done:** Cada imagen que referencia el informe (`{{plan:...}}` y las corridas del 1.5) tiene una entrada en el checklist con el nombre exacto que busca `build_informe.py`.

## Task 11 — Verificación de idempotencia (doble corrida completa)
**Prompts:** definition_of_done.md, constraints_reglas_catedra.md
**Context:** none
**Objective:** Confirmar que los 4 scripts corren dos veces seguidas sin errores y con resultados estables.
**Description:**
- Correr 00 → 01 → 02 → 03 dos veces seguidas con el runner.
- Comparar los CSV clave entre las dos corridas: conteos, top 10 y ancla idénticos; para los embeddings y el AUCPR, iguales o con una diferencia mínima documentada.
- Dejar el informe de la comparación.
**Outputs:**
- `docs/estado/verificacion_idempotencia.md` — creado (resultado de las dos corridas y diferencias, si las hay)
- `outputs/resultados/**` — reescrito por la segunda corrida
**Definition of done:** Las 8 ejecuciones terminan con código 0 y la nota no informa diferencias en los entregables deterministas.

## Task 12 — Informe PDF
**Prompts:** constraints_informe_entrega.md, constraints_evidencia_capturas.md, role.md, constraints_ejercicio_1.md, constraints_ejercicio_2.md, constraints_ejercicio_3.md, constraints_parte_comun.md
**Context:** CONSIGNA.md
**Objective:** Redactar la plantilla del informe y generar un PDF de 8 páginas o menos que cubra todos los entregables.
**Description:**
- **Estructura de `docs/informe/informe.md`:**
  - carátula breve (materia, TP 2, Trabajo 2, eje Drama, integrantes, docente y fecha);
  - entorno y carga;
  - parte común;
  - Ej. 1, 2 y 3: por cada punto, tabla o imagen con 2–4 líneas de interpretación y de decisiones (betweenness sin peso, LPA ponderado, FastRP para KNN, node2vec dentro del pipeline sin fuga, índice preexistente del dump, Eager);
  - anexo mínimo con los parámetros.
- **`src/tp2/build_informe.py`:**
  - reemplaza `{{tabla:<script>/<id>[:columnas][:n]}}` por una tabla markdown;
  - reemplaza `{{plan:<id>}}` por la captura del grupo si existe y, si no, por el render;
  - escribe `outputs/informe/informe_build.md`;
  - corre `pandoc` con `--pdf-engine=xelatex`, `geometry:margin=2cm`, `fontsize=10pt` y tablas compactas;
  - controla las páginas con `pdfinfo` y falla si pasan de 8.
- Mientras no haya capturas, el PDF sale con los renders y una marca discreta de "render de respaldo".
**Outputs:**
- `docs/informe/informe.md` — creado
- `src/tp2/build_informe.py` — creado
- `outputs/informe/informe_build.md`, `outputs/informe/TP2_Trabajo2_informe.pdf` — creados
**Definition of done:** `build_informe.py` termina con código 0. `pdfinfo` informa 8 páginas o menos. El PDF contiene cada entregable (1.1–1.5, 2.1–2.4, 3.1–3.4, C.1 y C.2) y los tres nombres del grupo.

## Task 13 — Zip de entrega
**Prompts:** constraints_informe_entrega.md, definition_of_done.md
**Context:** none
**Objective:** Generar el zip final con exactamente lo que pide la consigna.
**Description:**
- `src/tp2/armar_entrega.py` arma `outputs/entrega/TP2_Trabajo2_Adell_Giannice_Mazzola.zip` con `cypher/00_parte_comun.cypher`, `cypher/01_ejercicio1.cypher`, `cypher/02_ejercicio2.cypher`, `cypher/03_ejercicio3.cypher`, `notebook/ej3_4_pairre.ipynb` e `informe/TP2_Trabajo2_informe.pdf`.
- Falla si falta alguno o si el notebook no tiene salidas.
- Lista el contenido al terminar.
**Outputs:**
- `src/tp2/armar_entrega.py` — creado
- `outputs/entrega/TP2_Trabajo2_Adell_Giannice_Mazzola.zip` — creado
**Definition of done:** `python -m zipfile -l` muestra exactamente esos 6 archivos, sin `.env` ni nada del skill. El notebook dentro del zip tiene salidas.

## Task 14 — Integrar las capturas del grupo y regenerar
**Prompts:** constraints_evidencia_capturas.md, constraints_informe_entrega.md, constraints_proceso_repositorio.md
**Context:** none
**Objective:** Cuando el grupo deje las capturas en `outputs/capturas/`, regenerar el informe y el zip con las capturas reales.
**Description:**
- Es una pausa manual: el grupo sigue `docs/checklist_capturas.md`.
- Después: verificar que estén todos los nombres esperados, correr `build_informe.py` y `armar_entrega.py`, volver a controlar las 8 páginas y hacer el commit final.
- Si falta alguna captura, informarlo y dejar el render en su lugar.
**Outputs:**
- `outputs/informe/TP2_Trabajo2_informe.pdf` — regenerado
- `outputs/entrega/TP2_Trabajo2_Adell_Giannice_Mazzola.zip` — regenerado
- `docs/estado/entrega_final.md` — creado (checklist final: qué capturas son reales y cuáles son render, páginas y contenido del zip)
**Definition of done:** El PDF regenerado tiene 8 páginas o menos y usa las capturas reales en todas las imágenes que el grupo entregó. El zip vuelve a pasar el control de la Task 13.
