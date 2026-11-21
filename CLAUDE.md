# CLAUDE.md

Claude Code lee este archivo al empezar cada sesión en este repo.

TP 2 de *Bases de Datos Orientadas a Grafos* (UCA, 2C 2026). Trabajo 2: Adell, Giannice, Mazzola. Eje Drama.

## Project context

- **Plan:** `PLAN.md`, en la raíz. Las tareas se numeran del 1 al 14. Cada tarea indica en **Prompts** qué archivos de `prompts/` leer; leer esos y no todo.
- **Consigna:** `CONSIGNA.md` (Trabajo 2 + secciones comunes). El original está en `context/TP_2-2.pdf`.
- **Material de la cátedra:** `context/`. Unidad V es GDS (Ej. 1), Unidad VI son índices, planes y lotes (Ej. 2) y Unidad VII es ML en grafos y el notebook PyKEEN (Ej. 3). El estilo de los scripts sigue esas prácticas.
- **Estado del setup y relevamiento del esquema:** `docs/estado/setup_neo4j.md`.
- **Skill de planificación:** `.claude/skills/project_planner/`. No es parte de la entrega.

## Conventions

- **Todo lo que genera el código va en `outputs/`:** CSV, JSON, imágenes, TSV, modelos, PDF compilado y zip. No va junto al código fuente ni en `docs/`. `docs/` es solo para lo escrito a mano (informe fuente, checklist, notas de estado).
- **Neo4j:**
  - DBMS `tp2-recommendations` (2026.09.0, GDS y APOC 2026.09.0) en `neo4j://127.0.0.1:7687`. Tiene que estar iniciado en Neo4j Desktop; si la conexión falla, pedirle al usuario que lo inicie.
  - Ruta: `C:\Users\matia\.Neo4jDesktop2\Data\dbmss\dbms-cddf7c97-e694-49c1-93be-5a737fb31239`.
  - No tocar el DBMS `grafos-uca`.
- **Credenciales:**
  - Solo en `.env` (`NEO4J_PASSWORD`; `NEO4J_URI` y `NEO4J_USER` son opcionales).
  - Se leen siempre con `src/tp2/conexion.py`. Nunca imprimir la contraseña ni copiarla a otro archivo.
  - `.env` no va a git ni al zip.
- **Python:**
  - Siempre el env conda `grafos-tp2`: `conda run -n grafos-tp2 python ...`, con kernel `grafos-tp2` para el notebook.
  - No tocar el env `tp2`.
  - Comandos de módulo desde la raíz, por ejemplo `python -m src.tp2.run_cypher src/cypher/01_ejercicio1.cypher`.
  - ⚠️ La máquina tiene un `PYTHONPATH=D:\anaconda` global. Conviene invocar el intérprete del env directamente, sin ese valor, y con salida UTF-8: `env -u PYTHONPATH PYTHONIOENCODING=utf-8 /d/miniconda/envs/grafos-tp2/python.exe -m ...`.
  - `conda run` no acepta argumentos con saltos de línea: para Python multilínea, usar un archivo o un heredoc con el intérprete del env.
- **Comandos de punta a punta:**
  - Scripts: `python -m src.tp2.run_cypher src/cypher/<script>.cypher`.
  - Re-render de planes sin volver a ejecutar: `python -m src.tp2.planes outputs/resultados/02_ejercicio2`.
  - Notebook: `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=grafos-tp2 src/notebooks/ej3_4_pairre.ipynb`.
  - Informe: `python -m src.tp2.build_informe`.
  - Zip: `python -m src.tp2.armar_entrega`.
- **Disco:** C: está casi lleno (≈0,3 GB libres al 21/11). El DBMS y los temporales viven en C:. Para instalar con pip, usar `--no-cache-dir` y `TEMP`/`TMP` apuntando a D:.
- **Reproducibilidad GDS:** las proyecciones `califW` usan `readConcurrency: 1`. Betweenness, LPA, KNN, node2vec y la predicción de LP usan `concurrency: 1`: con varios hilos, la betweenness muestreada variaba entre corridas pese a la semilla (ver `docs/estado/verificacion_idempotencia.md`).
- **Scripts `.cypher`** (`src/cypher/00..03`):
  - Cada sentencia va precedida por `// @paso <id> [medir=N]`. El `<id>` sigue la consigna (`1.2_betweenness_top10`, `2.1_profile_sin_indice`, `C.6_recomendacion_base`).
  - El runner usa el id como nombre de archivo de salida, y el informe lo referencia con `{{tabla:<script>/<id>}}` y `{{plan:<id>}}`.
  - Una sentencia por paso, terminada en `;`, para que el archivo se pueda pegar entero en la app Query.
  - Cada script es idempotente: arranca con `gds.graph.drop(…, false)`, `gds.pipeline.drop(…, false)` y `gds.model.drop(…, false)`, y deshace las propiedades o índices que crea antes de volver a crearlos.
  - `CALL … IN TRANSACTIONS` necesita autocommit: el runner usa `session.run`. En Query anda sin `:auto`.
- **Reglas de la cátedra** (son parte de la nota):
  - `randomSeed: 42` (GDS) y `seed`/`random_state` 42 (Python) en todo lo que lo acepte.
  - Proyecciones UNDIRECTED.
  - Nombres fijos: `califW` y `ratingNorm`.
  - Embeddings de dimensión 128.
  - ML acotado a películas con ≥20 calificaciones.
- **Película ancla:** se calcula en cada consulta (Drama, más `RATED`, desempate por título). Hoy es *Forrest Gump*, pero nunca se hardcodea.
- **Idioma:** español rioplatense en comentarios, nombres libres e informe. Los nombres de algoritmos y de propiedades técnicas se mantienen (`betweenness`, `embFastRP`).
- **Git:** local, sin remoto. Un commit por tarea de PLAN.md, con un mensaje en español que nombre la tarea (`Task 6 — Ejercicio 1 (GDS sobre califW)`).

## How to verify a task is done

- Cada tarea tiene su **Definition of done** en PLAN.md.
- **Control global** de cualquier script Cypher: `conda run -n grafos-tp2 python -m src.tp2.run_cypher <script>` termina con código 0 y `outputs/resultados/<script>/_ejecucion.json` muestra todos los pasos en `ok`.
- **Control de cordura** antes de medir nada: `MATCH (n) RETURN count(n)` tiene que dar 28.863. Si da otra cosa, la base no es el dump original.

## Pasos manuales (solo los hace el grupo; frenar y pedirlos)

- Iniciar o detener el DBMS en Neo4j Desktop.
- Las capturas de Query según `docs/checklist_capturas.md`, guardadas en `outputs/capturas/`.
- Subir el zip al EVA (cierre: 23/11/2026, 23:59).

## Explicitly out of scope

- Lo de los otros trabajos (1 y 3–7): PageRank, closeness, Leiden, ArticleRank, WCC, eigenvector, clasificación de nodos, índices de texto, compuestos o token-lookup, `decada`, `SIMILAR_GENERO`, `ACTUO_CON`, `popularidad`, GraphSAGE y TransE.
- GraphRAG, Ollama y spaCy (texto → grafo).
- `LOAD CSV` y recargar la base de otra forma que no sea el dump.
- Repositorio remoto o GitHub.
- Extras que estiren el informe más allá de 8 páginas.
