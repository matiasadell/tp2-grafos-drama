---
title: "Trabajo Práctico 2 — Trabajo 2 (eje Drama)"
subtitle: "Bases de Datos Orientadas a Grafos · UCA · 2.º cuatrimestre 2026 · Docente: José Canelón"
author: "Matías Adell · Agustín Giannice · Facundo Mazzola"
date: "Noviembre de 2026"
lang: es
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
---

## Entorno, datos y método

- **Entorno.** Neo4j Desktop 2.2.1 con un DBMS local **Neo4j 2026.09.0 Enterprise**, **GDS 2026.09.0** y **APOC 2026.09.0** (heap de 4 GB, page cache de 1 GB). El notebook corre en un env conda en CPU (PyKEEN 1.11.1, torch 2.15 CPU).
- **Carga.** El grafo se restauró desde el volcado `recommendations-50.dump`, sin `LOAD CSV`. En Desktop 2 no existe la sección *Files*: se usó *Create instance* con el archivo del dump.
- **Scripts.** Los cuatro `.cypher` (parte común y Ej. 1–3) son **reejecutables**: arrancan liberando lo que crean (`gds.graph.drop`, `gds.pipeline.drop` y `gds.model.drop` con `false`) y deshacen propiedades e índices propios. Se ejecutaron paso a paso con un *runner* en Python (driver `neo4j`, en autocommit) que guarda cada resultado como evidencia.
- **Indicaciones.** Semilla 42 en todo lo que la acepta, proyecciones UNDIRECTED y los nombres de la consigna (`califW`, `ratingNorm`).
- **Película ancla.** La película de Drama con más `[:RATED]` es **Forrest Gump (1994)**, con 341 calificaciones. Se recalcula dentro de cada consulta; no está escrita a mano.

## Parte común — síntesis

**Panorama.** El grafo tiene **28.863 nodos y 166.261 relaciones**, que coinciden con la consigna: sí. Una `:Person` puede ser `:Actor` y `:Director` a la vez (487 lo son), por eso las etiquetas suman más que el total.

| Etiqueta | Nodos |
|---|---|
| Person | 19.047 |
| Actor | 15.443 |
| Movie | 9.125 |
| Director | 4.091 |
| User | 671 |
| Genre | 20 |

| Tipo de relación | Relaciones |
|---|---|
| RATED | 100.004 |
| ACTED_IN | 35.910 |
| IN_GENRE | 20.340 |
| DIRECTED | 10.007 |

**Las 3 películas con más calificaciones:**

| Película | Año | Calificaciones |
|---|---|---|
| Forrest Gump | 1994 | 341 |
| Pulp Fiction | 1994 | 324 |
| Shawshank Redemption, The | 1994 | 311 |

**Recomendación base (sin GDS) para la ancla.** Se usa el patrón `(:Movie)<-[:RATED]-(:User)-[:RATED]->(rec:Movie)`, ordenado por usuarios en común:

| Recomendación | Año | Usuarios en común |
|---|---|---|
| Pulp Fiction | 1994 | 231 |
| Silence of the Lambs, The | 1991 | 227 |
| Jurassic Park | 1993 | 221 |
| Shawshank Redemption, The | 1994 | 216 |
| Matrix, The | 1999 | 185 |
| Braveheart | 1995 | 184 |
| Terminator 2: Judgment Day | 1991 | 184 |
| Star Wars: Episode IV - A New Hope | 1977 | 182 |
| Schindler's List | 1993 | 177 |
| Toy Story | 1995 | 176 |

Es un filtrado colaborativo por co-ocurrencia: favorece los títulos muy populares de los noventa, que comparten público con *Forrest Gump*. No normaliza por popularidad.

## Ejercicio 1 — Graph Data Science sobre `califW`

**1.1 Proyección.** Se proyectó Usuario–Película desde `[:RATED]`, UNDIRECTED y con la propiedad `rating` como peso: **`califW` = 9.796 nodos y 200.008 relaciones**. Son 671 usuarios y 9.125 películas. El conteo de relaciones duplica las 100.004 `[:RATED]` porque cada arista no dirigida se guarda en ambos sentidos.

**1.2 Intermediación (betweenness).** Se usó muestreo (`samplingSize` 1000, `samplingSeed` 42, `concurrency` 1) y **sin peso**. GDS interpreta el peso como *costo* del camino, así que usar el rating haría que una calificación alta "alejara" a usuario y película, al revés de lo que significa. Top 10 (la Figura 1, en el 1.5, muestra la misma consulta en Query):

| Tipo | Nodo | Betweenness |
|---|---|---|
| User | Robert Brooks | 905.487 |
| User | Darlene Garcia | 603.275 |
| User | Karen Avila | 316.053 |
| User | Angela Robertson | 269.168 |
| User | Angela Garcia | 264.897 |
| User | Larry Boyd | 241.802 |
| User | Marissa Choi | 195.752 |
| User | Rita Owens | 192.878 |
| User | Aaron Castro | 154.595 |
| User | Crystal Spencer | 153.986 |

Los diez son usuarios, y coinciden con los más activos: *Darlene Garcia* tiene 2.391 calificaciones y *Robert Brooks*, 1.868. En un grafo bipartito, los caminos entre películas pasan por usuarios; los que calificaron mucho, incluidos títulos poco vistos, son los puentes obligados. Con muestreo los valores son una aproximación. Con varios hilos, la selección de nodos fuente variaba entre corridas a pesar de la semilla (hasta un 2 %); con `concurrency` 1 el resultado es idéntico en cada corrida.

**1.3 Label Propagation (ponderado por rating).** Hay **60 comunidades**. El algoritmo convergió en 4 iteraciones, con `concurrency` 1 para que sea reproducible. Las 5 mayores:

| Puesto | Comunidad | Tamaño | Usuarios | Películas |
|---|---|---|---|---|
| 1 | 9148 | 9.737 | 671 | 9.066 |
| 2 | 3712 | 1 | 0 | 1 |
| 3 | 3751 | 1 | 0 | 1 |
| 4 | 4002 | 1 | 0 | 1 |
| 5 | 4066 | 1 | 0 | 1 |

El resultado es casi trivial: una comunidad gigante con los 671 usuarios y 9.066 películas, más 59 *singletons*, que son exactamente las 59 películas que nadie calificó y quedan aisladas en la proyección. El grafo de calificaciones es una única componente muy densa (unas 149 calificaciones por usuario). Los pesos son todos positivos (de 0,5 a 5), así que solo modulan la votación y LPA converge a la etiqueta dominante. Para este grafo, LPA no encuentra estructura de comunidades.

**1.4 KNN sobre un embedding de usuarios.** El embedding es **FastRP** (dimensión 128, semilla 42, ponderado por rating), agregado a `califW` con `mutate`. KNN se corrió solo sobre `:User` (coseno, `topK` 10, semilla 42 y `concurrency` 1). Los pares se normalizaron y se deduplicaron, sin autosimilitud:

| Usuario 1 | Usuario 2 | Similitud |
|---|---|---|
| Aaron Nelson | Katie Collins | 0,9981 |
| Aaron Nelson | Robert Davis | 0,9978 |
| Robert Davis | Katie Collins | 0,9977 |
| Christopher Sanders | Aaron Nelson | 0,9974 |
| Robin Smith | Aaron Nelson | 0,9970 |
| Aaron Nelson | Joseph Berry | 0,9963 |
| Brian Smith | Christopher Sanders | 0,9963 |
| Brian Smith | Heather Morrison | 0,9962 |
| Theodore Landry | Gary Tucker | 0,9962 |
| Robin Smith | Robert Davis | 0,9961 |

Las similitudes son muy altas (cerca de 0,997). FastRP promedia vecindarios y, en un grafo tan denso, los embeddings de los usuarios quedan concentrados. El ranking sirve igual para ordenar perfiles cercanos (*Aaron Nelson* aparece como "centro" de varios pares).

**1.5 Betweenness en los modos stream, stats y write.** Se usaron los mismos parámetros que en el 1.2. El modo **write persiste la propiedad de nodo `betweenness`** en 9.796 nodos. La verificación en la base coincide con el top del modo stream.

![1.5 — modo stream](img01.png){width=7.1cm}

![1.5 — modo stats](img02.png){width=10.2cm}

![1.5 — modo write](img03.png){width=8.7cm}

## Ejercicio 2 — Índices, planes y escritura por lotes

La consulta es `MATCH (m:Movie) WHERE m.year >= 1990 AND m.year <= 1999 RETURN count(m)`, que devuelve 2.202 películas. **El dump ya trae un índice RANGE sobre `Movie(year)`** (`index_fc5f831e`). Para medir "sin el índice específico", el script primero lo borra y controla que no quede ninguno sobre `year`. Los tiempos del texto son la mediana de 20 corridas después de un calentamiento. Cada captura muestra una corrida suelta en Query, así que sus tiempos pueden diferir un poco; los db hits y los operadores son los mismos.

**2.1 Sin índice.** El operador inicial es **NodeByLabelScan** (recorre las 9.125 `:Movie`), seguido de `Filter`: **18.222 db hits**, 9,0 ms de punta a punta y 6,89 ms de operadores.

![2.1 — PROFILE sin índice](img04.png){width=13.6cm}

**2.2 Con índice de rango `movie_year_range`.** El plan pasa a **NodeIndexSeekByRange**, que lee solo las entradas del rango: **2.203 db hits**, 2,0 ms de punta a punta y 0,73 ms de operadores.

![2.2 — PROFILE con índice de rango](img05.png){width=16.2cm}

| Factor de mejora (sin índice / con índice) | Valor |
|---|---|
| db hits | **8,3×** |
| Tiempo de operadores (PROFILE) | **9,4×** |
| Tiempo de punta a punta (cliente) | 4,5× |

La mejora en el motor (db hits y tiempo de operadores) es de casi un orden de magnitud. De punta a punta es menor porque, con solo 9.125 películas, pesa el costo fijo del ida y vuelta con el servidor.

**2.3 EXPLAIN, runtime y Eager.** `EXPLAIN` muestra el plan estimado sin ejecutar (sin filas ni db hits reales). `PROFILE` confirma el **runtime PIPELINED** (planner COST, Cypher 25). En la consulta de rango **no aparece Eager**, como se esperaba en una lectura pura. Se analizó también la sentencia de escritura del 2.4: su plan (`TransactionForeach` → `Expand` → `EagerAggregation` → `Unwind` → `SetProperty`) **tampoco tiene un operador Eager**, porque lee `rating` y escribe otra propiedad, `ratingNorm`, así que no hay conflicto de lectura y escritura. `EagerAggregation` es la agregación que calcula el promedio, no la barrera Eager.

![2.3 — EXPLAIN de la consulta de rango](img06.png){width=10.1cm}

![2.3 — PROFILE de la consulta de rango (runtime)](img07.png){width=16.2cm}

![2.3 — EXPLAIN de la escritura del 2.4](img08.png){width=8.8cm}

**2.4 Escritura por lotes: `ratingNorm`.** Cada lote procesa 50 usuarios con todas sus calificaciones. El promedio del usuario se calcula dentro de la transacción del lote:

```
MATCH (u:User)
CALL (u) {
  MATCH (u)-[r:RATED]->(:Movie)
  WITH collect(r) AS calificaciones, avg(r.rating) AS promedio
  UNWIND calificaciones AS r
  SET r.ratingNorm = r.rating - promedio
} IN TRANSACTIONS OF 50 ROWS;
```

Verificación: todas las `[:RATED]` quedaron normalizadas y el promedio de `ratingNorm` es 0, tanto global como por usuario.

| RATED | Con ratingNorm | Promedio global | Mínimo | Máximo |
|---|---|---|---|---|
| 100.004 | 100.004 | 0,000 | -4,031 | 3,541 |

| Usuario | Calificaciones | Promedio rating | Promedio ratingNorm |
|---|---|---|---|
| Darlene Garcia | 2.391 | 3,367 | 0,000 |
| Robert Brooks | 1.868 | 3,552 | 0,000 |
| Karen Avila | 1.735 | 2,894 | 0,000 |
| Angela Garcia | 1.700 | 2,622 | 0,000 |
| Angela Robertson | 1.610 | 3,374 | 0,000 |

## Ejercicio 3 — Embeddings, predicción de enlaces y PairRE

**3.1 node2vec sobre `califW`.** Configuración: dimensión 128, `walkLength` 40, `walksPerNode` 10, una iteración, caminatas sesgadas por el peso `rating`, semilla 42 y `concurrency` 1. Se muestran 5 nodos (la ancla, la película más calificada que no es la ancla y los 3 usuarios más activos), con las primeras 6 de sus **128 componentes**. Los vectores completos están en el Anexo:

| Tipo | Nodo | Dim. | Embedding (primeras 6 componentes) |
|---|---|---|---|
| Movie | Forrest Gump | 128 | [0,146, -0,133, 0,241, 0,064, -0,284, 0,047, …] (dim 128) |
| Movie | Pulp Fiction | 128 | [0,271, -0,089, 0,197, 0,052, -0,096, -0,022, …] (dim 128) |
| User | Darlene Garcia | 128 | [-0,796, -0,088, 0,122, -0,281, 0,279, 0,095, …] (dim 128) |
| User | Karen Avila | 128 | [-0,610, -0,194, 0,113, 0,071, -0,130, 0,112, …] (dim 128) |
| User | Robert Brooks | 128 | [0,109, -0,104, 0,078, 0,055, -0,048, 0,368, …] (dim 128) |

**3.2 Objetivo y subgrafo de entrenamiento.** Se predicen nuevas `[:RATED]` usuario→película. El subgrafo se acotó, según las NOTAS, a las películas con al menos 20 calificaciones (proyección Cypher `califLP`): **1.974 nodos** (671 usuarios y 1.303 películas) y **69.104 relaciones `[:RATED]`**. GDS informa 138.208, porque cada arista no dirigida cuenta dos veces. Dentro del pipeline, el split del 3.3 reparte esas relaciones así: ≈10 % para test (≈6.910), ≈10 % del resto como ejemplos positivos de entrenamiento del clasificador (≈6.220) y el resto (≈55.970) como grafo de features, sobre el que se calcula node2vec.

**3.3 Pipeline de link prediction.** node2vec es un **paso del pipeline** (`addNodeProperty`): GDS lo recalcula sobre el grafo de entrenamiento, así que las aristas de test no se filtran al embedding. La feature es el producto de Hadamard de los embeddings. Split: 10 % test, 10 % train del resto y 3 folds de validación, con muestreo negativo 1:1. Candidatos: regresión logística (`penalty` 0, 0,01 y 0,1) y Random Forest (10 árboles con profundidad 10, y 25 con profundidad 15). Métrica: AUCPR.

| Modelo candidato | AUCPR validación (media de 3 folds) |
|---|---|
| Regresión logística, `penalty` 0 / 0,01 / 0,1 | 0,677 / 0,677 / 0,677 |
| Random Forest, 10 árboles y profundidad 10 | 0,815 |
| **Random Forest, 25 árboles y profundidad 15 (ganador)** | **0,834** |

**AUCPR de test = 0,832** (en *outer-train*: 0,967). Con un negativo por cada positivo, un clasificador al azar daría ≈0,5. La regresión logística no logra separar bien el producto de Hadamard (≈0,68); el bosque captura interacciones entre componentes y gana con margen, aunque la brecha entre train y test muestra algo de sobreajuste. El Random Forest devuelve la fracción de árboles que votan "sí": **34 pares nuevos** (de 27 usuarios) empatan con probabilidad ≥ 0,999. El top 5, obtenido con `concurrency` 1 para que sea reproducible, es una selección entre esos empatados. Ninguno de los pares existe en la base:

| Usuario | Película | Año | Probabilidad | ¿Ya existe? |
|---|---|---|---|---|
| Frank Davis | Jungle Book, The | 1967 | 1,0000 | no |
| Matthew Dudley | Parent Trap, The | 1961 | 1,0000 | no |
| Mrs. Lisa Bradshaw | Hurricane, The | 1999 | 1,0000 | no |
| Mrs. Lisa Bradshaw | Jacob's Ladder | 1990 | 1,0000 | no |
| Valerie Jackson | My Fair Lady | 1964 | 1,0000 | no |

**3.4 Completado de KG con PairRE** (notebook `ej3_4_pairre.ipynb`). Se usaron las tripletas `IN_GENRE` y `ACTED_IN` de las películas con al menos 20 calificaciones: 8.719 tripletas y 4.052 entidades, con split 80/10/10 y semilla 42. PairRE se entrenó con dimensión 128 y 100 épocas, en CPU. En test filtrado: **MRR = 0,105** y **Hits@10 = 0,192**. Hechos propuestos, `(película, IN_GENRE, Drama)`, entre películas que hoy no son Drama:

| Película | Género propuesto | Score | Géneros actuales |
|---|---|---|---|
| Vanilla Sky (2001) | Drama | -2,569 | Mystery, Romance, Sci-Fi, Thriller |
| African Queen, The (1951) | Drama | -2,592 | Adventure, Comedy, Romance, War |
| Devil in a Blue Dress (1995) | Drama | -2,609 | Crime, Film-Noir, Mystery, Thriller |

Un ranking al azar daría Hits@10 ≈ 10/4.052 ≈ 0,0025, así que el modelo es unas 75 veces mejor. Igual, el valor queda lejos del dataset *Nations* de la práctica (MRR ≈ 0,73) porque este KG es **ralo**: unas 2,2 tripletas por entidad, y la mayoría de los actores aparece una o dos veces. La pérdida converge hacia la época 20. Los tres hechos propuestos son plausibles: *Vanilla Sky* suele describirse como drama psicológico, *The African Queen* como aventura romántica con mucho de drama, y *Devil in a Blue Dress* como drama criminal neo-noir. Se verificó contra Neo4j que hoy ninguna de las tres tiene el género Drama. El score de PairRE es una distancia con signo negativo: más alto es más plausible.

## Anexo — Vectores node2vec completos (punto 3.1)

Los 5 vectores de dimensión 128 del punto 3.1, con 2 decimales. Salen del paso `3.1_node2vec_5_nodos` de `03_ejercicio3.cypher` (semilla 42, `concurrency` 1, reproducibles).

\begin{footnotesize}\sloppy
\noindent\textbf{Forrest Gump (Movie)}, dim 128: 0,15 -0,13 0,24 0,06 -0,28 0,05 0,00 0,57 -0,20 0,26 -0,23 -0,43 0,55 -0,28 0,04 -0,12 -0,10 0,37 -0,15 -0,06 0,25 0,09 0,02 0,19 -0,30 -0,04 -0,11 -0,23 -0,15 -0,09 -0,13 -0,11 0,31 -0,18 -0,26 -0,00 0,03 -0,16 0,22 -0,02 0,44 -0,45 0,09 -0,22 0,12 -0,22 -0,25 0,10 0,49 0,30 0,32 -0,29 0,29 0,48 0,14 -0,07 -0,04 0,13 0,09 -0,02 -0,36 0,24 0,23 -0,26 -0,22 -0,29 0,38 0,27 -0,30 0,23 -0,12 -0,10 -0,01 0,03 -0,46 0,04 0,20 -0,02 -0,06 0,02 0,05 0,01 -0,14 -0,20 -0,00 0,12 -0,09 0,44 0,41 -0,18 -0,21 -0,22 0,11 0,49 -0,18 0,03 -0,25 -0,12 0,21 -0,25 0,17 0,19 0,21 0,29 0,23 -0,15 -0,12 -0,16 -0,22 0,07 0,53 -0,12 0,10 -0,32 -0,20 -0,01 -0,06 -0,00 -0,34 0,12 -0,29 0,39 -0,58 -0,05 -0,04 0,09 0,23 -0,35\par\smallskip
\noindent\textbf{Pulp Fiction (Movie)}, dim 128: 0,27 -0,09 0,20 0,05 -0,10 -0,02 -0,09 0,27 -0,13 0,01 -0,17 -0,01 0,35 -0,02 -0,23 -0,14 0,18 0,19 -0,27 -0,15 -0,03 -0,25 0,15 0,16 -0,24 -0,05 -0,23 0,07 -0,35 -0,41 -0,27 -0,56 0,17 -0,00 -0,25 0,26 -0,05 0,13 -0,18 -0,15 0,02 -0,29 -0,06 -0,17 0,36 -0,18 -0,22 -0,07 0,43 0,23 0,28 -0,23 0,36 0,28 -0,02 -0,08 0,19 0,51 0,10 -0,00 -0,13 0,13 -0,04 -0,23 -0,14 -0,31 0,03 0,13 -0,52 -0,04 0,07 -0,19 -0,01 -0,10 -0,15 -0,13 0,25 0,15 -0,15 0,07 -0,20 -0,48 0,03 0,12 0,01 0,15 0,09 0,46 -0,08 -0,04 -0,05 0,15 -0,16 0,55 0,12 -0,29 -0,34 0,12 0,21 -0,33 -0,09 -0,02 0,39 0,41 0,27 -0,21 -0,05 -0,24 -0,24 -0,13 0,33 -0,05 0,44 0,19 -0,59 0,23 -0,15 -0,00 -0,21 -0,23 -0,27 0,12 -0,22 -0,07 -0,05 -0,04 0,39 0,05\par\smallskip
\noindent\textbf{Darlene Garcia (User)}, dim 128: -0,80 -0,09 0,12 -0,28 0,28 0,09 -0,50 -0,07 0,09 0,52 0,00 0,61 0,32 0,27 0,12 -0,17 0,04 0,12 -0,29 -0,13 0,34 0,14 0,29 0,26 -0,24 0,33 -0,10 0,38 -0,67 -0,33 -0,21 0,32 0,19 0,21 0,30 -0,16 0,14 0,59 0,36 0,40 -0,07 -0,22 -0,29 -0,07 -0,12 -0,08 -0,24 -0,17 0,79 -0,07 0,21 0,12 0,19 0,05 -0,14 0,05 -0,30 0,23 -0,12 -0,33 -0,06 0,10 -0,21 -0,19 0,02 -0,28 -0,24 -0,07 0,26 -0,24 0,06 0,08 -0,10 0,19 -0,18 0,28 0,22 0,05 0,22 0,45 0,04 -0,04 0,10 -0,10 0,34 0,33 -0,15 0,30 -0,45 -0,24 -0,16 -0,25 -0,57 0,26 0,04 0,11 -0,06 -0,11 0,20 -0,39 0,10 0,48 -0,15 0,14 -0,11 0,02 -0,13 -0,55 0,18 -0,15 0,36 0,52 0,10 0,06 0,21 0,29 -0,27 0,00 0,44 0,42 -0,24 0,08 -0,05 0,40 0,39 0,08 -0,37 -0,41\par\smallskip
\noindent\textbf{Karen Avila (User)}, dim 128: -0,61 -0,19 0,11 0,07 -0,13 0,11 0,14 0,19 0,17 -0,13 -0,26 0,15 0,41 -0,25 -0,12 0,02 0,34 -0,26 0,17 -0,18 -0,23 -0,05 -0,14 -0,31 -0,42 0,10 0,44 -0,09 -0,12 0,14 0,30 0,05 -0,02 -0,15 0,01 -0,12 0,35 0,16 0,14 -0,35 0,13 0,11 -0,16 0,33 0,04 0,13 0,05 0,36 1,00 0,60 0,12 -0,43 0,10 -0,18 0,54 0,52 0,12 -0,19 -0,10 -0,71 0,04 0,34 0,21 -0,13 0,44 -0,45 -0,09 -0,05 -0,89 -0,47 -0,16 -0,40 0,28 0,29 -0,04 0,31 0,36 -0,14 -0,12 0,14 -0,22 0,21 0,32 -0,12 0,24 0,34 -0,24 0,37 0,32 -0,17 -0,14 -0,23 -0,09 0,23 0,02 -0,43 -0,34 -0,06 -0,06 -0,69 -0,26 -0,22 0,47 0,17 0,20 0,30 0,10 0,01 -0,12 0,50 -0,37 0,19 -0,42 -0,42 -0,23 -0,30 -0,23 -0,16 -0,09 -0,38 -0,19 0,10 -0,25 0,04 -0,29 0,15 0,12 -0,15\par\smallskip
\noindent\textbf{Robert Brooks (User)}, dim 128: 0,11 -0,10 0,08 0,06 -0,05 0,37 0,08 0,11 0,26 0,41 0,02 -0,11 0,45 -0,30 -0,22 0,29 0,19 0,11 -0,01 -0,00 0,32 0,02 0,05 -0,04 0,11 0,20 -0,09 -0,17 -0,17 0,13 -0,03 0,02 -0,18 -0,22 -0,13 0,46 0,10 0,28 0,45 -0,17 0,45 -0,25 0,07 -0,06 -0,04 0,26 0,10 -0,16 0,76 0,04 0,08 -0,13 0,28 -0,25 -0,29 -0,15 0,09 -0,10 0,38 -0,07 0,01 0,14 0,42 -0,18 -0,20 -0,14 -0,10 0,21 -0,52 -0,12 -0,13 0,05 -0,16 0,64 0,05 -0,04 0,26 -0,17 -0,09 -0,22 -0,06 0,06 -0,32 0,16 0,07 0,26 -0,17 0,06 -0,29 -0,16 0,24 -0,35 0,22 0,40 0,11 -0,03 -0,51 0,05 0,24 -0,57 -0,08 -0,24 -0,09 -0,24 0,12 0,07 -0,04 0,14 -0,49 0,04 -0,03 0,33 0,27 0,13 -0,17 0,06 -0,17 0,18 -0,08 -0,29 0,62 -0,01 -0,18 -0,06 0,36 -0,14 0,08 -0,26\par\smallskip
\end{footnotesize}
