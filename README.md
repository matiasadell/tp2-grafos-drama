# TP 2 — Bases de Datos Orientadas a Grafos · Trabajo 2 (eje Drama)

**UCA · 2.º cuatrimestre 2026 · Docente: José Canelón**
**Integrantes:** Matías Adell · Agustín Giannice · Facundo Mazzola

Resolución del Trabajo Práctico 2 (Unidades V, VI y VII) sobre el grafo de recomendaciones de Neo4j (MovieLens + OMDb):

- **Parte común:** panorama del grafo y recomendación base sin GDS.
- **Ejercicio 1:** Graph Data Science sobre la proyección `califW`.
- **Ejercicio 2:** índices, planes de ejecución y escritura por lotes.
- **Ejercicio 3:** embeddings, predicción de enlaces y completado de knowledge graph con PairRE.

La consigna está en [`CONSIGNA.md`](CONSIGNA.md) y el informe, en [`outputs/informe/TP2_Trabajo2_informe.pdf`](outputs/informe/TP2_Trabajo2_informe.pdf).

## Resultados principales

| Punto | Resultado |
|---|---|
| Parte común | 28.863 nodos y 166.261 relaciones (coincide con la consigna). Película ancla: *Forrest Gump* (1994), 341 calificaciones |
| 1.1 Proyección `califW` | 9.796 nodos y 200.008 relaciones (UNDIRECTED, ponderada por `rating`) |
| 1.3 Label Propagation | 60 comunidades: una gigante más 59 películas sin calificaciones |
| 2.1 → 2.2 Índice RANGE sobre `Movie.year` | 18.222 → 2.203 db hits (8,3×); tiempo de operadores 9,4× menor |
| 2.3 | Runtime PIPELINED, sin operador Eager (ni en la lectura ni en la escritura del 2.4) |
| 3.3 Link prediction | AUCPR de test 0,832 (gana Random Forest con 25 árboles; la regresión logística queda en ≈0,68) |
| 3.4 PairRE | MRR 0,105 y Hits@10 0,192. Propone como Drama: *Vanilla Sky*, *The African Queen* y *Devil in a Blue Dress* |

Los cuatro scripts se corrieron dos veces seguidas y dieron resultados idénticos (ver [`docs/estado/verificacion_idempotencia.md`](docs/estado/verificacion_idempotencia.md)).

## Estructura

```
src/cypher/          00_parte_comun, 01_ejercicio1, 02_ejercicio2, 03_ejercicio3 (.cypher, reejecutables)
src/notebooks/       ej3_4_pairre.ipynb (PyKEEN, ejecutado)
src/tp2/             runner de Cypher, render de planes, armado del informe y del zip
outputs/resultados/  evidencia de cada paso (CSV + JSON con contadores, tiempos y planes)
outputs/planes/      renders de los planes PROFILE/EXPLAIN
outputs/kg/          tripletas, métricas y hechos propuestos por PairRE
outputs/capturas/    capturas de la app Query (las saca el grupo)
docs/                plantilla del informe, checklist de capturas y notas de estado
context/             material de la cátedra (consigna original y prácticas)
PLAN.md, CLAUDE.md, prompts/   plan de trabajo (generado con el skill project_planner, en .claude/skills/)
```

## Cómo reproducir

1. **Neo4j:** Neo4j Desktop 2 con un DBMS 2026.09.0 creado desde [`recommendations-50.dump`](https://github.com/neo4j-graph-examples/recommendations/raw/main/data/recommendations-50.dump) (*Create instance* con el archivo) y los plugins **GDS** y **APOC**. Se recomienda un heap de 4 GB.
2. **Credenciales:** crear `.env` en la raíz con `NEO4J_PASSWORD=<contraseña>` (opcionalmente `NEO4J_URI` y `NEO4J_USER`).
3. **Python:** `conda env create -f environment.yml`. Usa torch en CPU y no necesita GPU.
4. **Ejecutar**, desde la raíz y con el env `grafos-tp2`:
   ```bash
   python -m src.tp2.run_cypher src/cypher/00_parte_comun.cypher   # idem 01, 02 y 03
   jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=grafos-tp2 src/notebooks/ej3_4_pairre.ipynb
   python -m src.tp2.build_informe     # PDF con pandoc + xelatex
   python -m src.tp2.armar_entrega     # zip de entrega
   ```

Los scripts también se pueden pegar enteros en la app **Query** de Neo4j Desktop. Se usa semilla 42 en todo lo que la acepta; las proyecciones son UNDIRECTED y la betweenness corre con `concurrency: 1` para que sea reproducible.
