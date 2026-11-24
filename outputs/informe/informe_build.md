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

```{=latex}
\begin{minipage}[t]{0.44\textwidth}\centering
\begin{tabular}[t]{ll}
\toprule
Etiqueta & Nodos \\
\midrule
Person & 19.047 \\
Actor & 15.443 \\
Movie & 9.125 \\
Director & 4.091 \\
User & 671 \\
Genre & 20 \\
\bottomrule
\end{tabular}
\end{minipage}
\hfill
\begin{minipage}[t]{0.44\textwidth}\centering
\begin{tabular}[t]{ll}
\toprule
Tipo de relación & Relaciones \\
\midrule
RATED & 100.004 \\
ACTED\_IN & 35.910 \\
IN\_GENRE & 20.340 \\
DIRECTED & 10.007 \\
\bottomrule
\end{tabular}
\end{minipage}
```

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

**1.2 Intermediación (betweenness).** Se usó muestreo (`samplingSize` 1000, `samplingSeed` 42, `concurrency` 1) y **sin peso**. GDS interpreta el peso como *costo* del camino, así que usar el rating haría que una calificación alta "alejara" a usuario y película, al revés de lo que significa. El top 10 se ve en la Figura 1 (punto 1.5, modo stream), que usa esta misma consulta.

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

![1.5 — modo stream](img01.png){width=100%}

![1.5 — modo stats](img02.png){width=100%}

![1.5 — modo write](img03.png){width=100%}

\newpage

## Ejercicio 2 — Índices, planes y escritura por lotes

La consulta es `MATCH (m:Movie) WHERE m.year >= 1990 AND m.year <= 1999 RETURN count(m)`, que devuelve 2.202 películas. **El dump ya trae un índice RANGE sobre `Movie(year)`** (`index_fc5f831e`). Para medir "sin el índice específico", el script primero lo borra y controla que no quede ninguno sobre `year`. Los tiempos son la mediana de 20 corridas después de un calentamiento.

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

**3.1 node2vec sobre `califW`.** Configuración: dimensión 128, `walkLength` 40, `walksPerNode` 10, una iteración, caminatas sesgadas por el peso `rating`, semilla 42 y `concurrency` 1. Se muestran 5 nodos (la ancla, la película más calificada que no es la ancla y los 3 usuarios más activos). Cada vector tiene **128 componentes** y se referencia con una variable $\mathbf{v}_i$; debajo de la tabla están los vectores completos (3 decimales):

| Tipo | Nodo | Dimensión | Vector |
|---|---|---|---|
| Movie | Forrest Gump | 128 | $\mathbf{v}_{1}$ |
| Movie | Pulp Fiction | 128 | $\mathbf{v}_{2}$ |
| User | Darlene Garcia | 128 | $\mathbf{v}_{3}$ |
| User | Karen Avila | 128 | $\mathbf{v}_{4}$ |
| User | Robert Brooks | 128 | $\mathbf{v}_{5}$ |

\begin{footnotesize}\sloppy
\noindent$\mathbf{v}_{1}$ (Forrest Gump, dim 128) $=$ [0,146; -0,133; 0,241; 0,064; -0,284; 0,047; 0,003; 0,569; -0,202; 0,263; -0,233; -0,426; 0,550; -0,284; 0,044; -0,120; -0,099; 0,368; -0,150; -0,060; 0,247; 0,086; 0,020; 0,185; -0,302; -0,039; -0,110; -0,231; -0,149; -0,092; -0,129; -0,110; 0,314; -0,183; -0,264; -0,004; 0,035; -0,158; 0,217; -0,024; 0,436; -0,447; 0,087; -0,218; 0,123; -0,221; -0,251; 0,102; 0,487; 0,296; 0,324; -0,288; 0,287; 0,476; 0,144; -0,069; -0,043; 0,133; 0,087; -0,017; -0,357; 0,236; 0,231; -0,264; -0,225; -0,292; 0,382; 0,274; -0,299; 0,230; -0,117; -0,097; -0,014; 0,026; -0,460; 0,036; 0,198; -0,017; -0,059; 0,016; 0,048; 0,005; -0,136; -0,196; -0,001; 0,123; -0,094; 0,436; 0,409; -0,180; -0,214; -0,221; 0,115; 0,493; -0,181; 0,033; -0,247; -0,125; 0,214; -0,250; 0,167; 0,194; 0,208; 0,292; 0,233; -0,155; -0,117; -0,159; -0,222; 0,071; 0,530; -0,124; 0,099; -0,315; -0,199; -0,008; -0,064; -0,004; -0,338; 0,120; -0,287; 0,388; -0,583; -0,053; -0,042; 0,093; 0,235; -0,351]\par\smallskip
\noindent$\mathbf{v}_{2}$ (Pulp Fiction, dim 128) $=$ [0,271; -0,089; 0,197; 0,052; -0,096; -0,022; -0,089; 0,267; -0,130; 0,009; -0,172; -0,012; 0,354; -0,018; -0,227; -0,136; 0,182; 0,190; -0,271; -0,151; -0,030; -0,247; 0,147; 0,160; -0,242; -0,046; -0,226; 0,066; -0,354; -0,412; -0,267; -0,559; 0,168; -0,001; -0,254; 0,258; -0,051; 0,132; -0,182; -0,155; 0,022; -0,287; -0,060; -0,172; 0,356; -0,180; -0,225; -0,066; 0,431; 0,226; 0,280; -0,235; 0,355; 0,279; -0,021; -0,077; 0,189; 0,510; 0,101; -0,003; -0,129; 0,132; -0,044; -0,228; -0,144; -0,310; 0,029; 0,125; -0,517; -0,035; 0,071; -0,194; -0,007; -0,105; -0,154; -0,132; 0,248; 0,153; -0,150; 0,071; -0,198; -0,483; 0,034; 0,118; 0,013; 0,147; 0,095; 0,462; -0,081; -0,044; -0,052; 0,155; -0,165; 0,550; 0,120; -0,289; -0,342; 0,124; 0,205; -0,327; -0,086; -0,020; 0,387; 0,411; 0,271; -0,207; -0,051; -0,240; -0,235; -0,127; 0,329; -0,055; 0,444; 0,187; -0,589; 0,226; -0,153; -0,003; -0,208; -0,230; -0,269; 0,121; -0,221; -0,069; -0,049; -0,037; 0,387; 0,054]\par\smallskip
\noindent$\mathbf{v}_{3}$ (Darlene Garcia, dim 128) $=$ [-0,796; -0,088; 0,122; -0,281; 0,279; 0,095; -0,504; -0,065; 0,088; 0,519; 0,001; 0,608; 0,320; 0,266; 0,115; -0,169; 0,040; 0,122; -0,290; -0,131; 0,339; 0,144; 0,286; 0,257; -0,238; 0,331; -0,098; 0,381; -0,674; -0,333; -0,207; 0,318; 0,188; 0,208; 0,297; -0,156; 0,141; 0,587; 0,363; 0,404; -0,067; -0,222; -0,293; -0,074; -0,123; -0,081; -0,242; -0,175; 0,787; -0,065; 0,208; 0,122; 0,189; 0,054; -0,142; 0,055; -0,298; 0,234; -0,118; -0,331; -0,057; 0,102; -0,212; -0,188; 0,020; -0,276; -0,244; -0,066; 0,262; -0,244; 0,057; 0,085; -0,097; 0,192; -0,175; 0,283; 0,220; 0,049; 0,217; 0,445; 0,038; -0,038; 0,098; -0,102; 0,340; 0,334; -0,146; 0,304; -0,453; -0,236; -0,156; -0,251; -0,565; 0,261; 0,044; 0,105; -0,062; -0,109; 0,199; -0,392; 0,104; 0,485; -0,149; 0,142; -0,110; 0,025; -0,134; -0,555; 0,180; -0,146; 0,363; 0,521; 0,104; 0,056; 0,208; 0,287; -0,275; 0,005; 0,437; 0,423; -0,244; 0,076; -0,047; 0,402; 0,388; 0,082; -0,371; -0,410]\par\smallskip
\noindent$\mathbf{v}_{4}$ (Karen Avila, dim 128) $=$ [-0,610; -0,194; 0,113; 0,071; -0,130; 0,112; 0,139; 0,193; 0,174; -0,128; -0,262; 0,151; 0,412; -0,251; -0,120; 0,021; 0,335; -0,264; 0,174; -0,184; -0,231; -0,053; -0,139; -0,307; -0,418; 0,095; 0,435; -0,088; -0,125; 0,143; 0,303; 0,055; -0,018; -0,149; 0,013; -0,120; 0,353; 0,164; 0,142; -0,350; 0,127; 0,112; -0,159; 0,329; 0,036; 0,129; 0,048; 0,362; 0,999; 0,599; 0,118; -0,429; 0,102; -0,184; 0,540; 0,524; 0,123; -0,187; -0,097; -0,712; 0,043; 0,340; 0,214; -0,132; 0,438; -0,451; -0,087; -0,053; -0,890; -0,471; -0,156; -0,404; 0,281; 0,287; -0,044; 0,313; 0,357; -0,142; -0,123; 0,138; -0,217; 0,215; 0,319; -0,116; 0,243; 0,339; -0,237; 0,373; 0,322; -0,169; -0,141; -0,234; -0,092; 0,233; 0,019; -0,432; -0,338; -0,058; -0,057; -0,693; -0,264; -0,216; 0,465; 0,175; 0,202; 0,302; 0,103; 0,011; -0,115; 0,496; -0,367; 0,187; -0,418; -0,417; -0,234; -0,295; -0,227; -0,158; -0,086; -0,382; -0,185; 0,103; -0,249; 0,041; -0,290; 0,152; 0,118; -0,148]\par\smallskip
\noindent$\mathbf{v}_{5}$ (Robert Brooks, dim 128) $=$ [0,109; -0,104; 0,078; 0,055; -0,048; 0,368; 0,082; 0,112; 0,258; 0,407; 0,024; -0,113; 0,453; -0,303; -0,215; 0,287; 0,187; 0,106; -0,014; -0,004; 0,317; 0,019; 0,052; -0,037; 0,106; 0,203; -0,094; -0,173; -0,175; 0,125; -0,035; 0,021; -0,177; -0,223; -0,126; 0,458; 0,099; 0,275; 0,451; -0,168; 0,447; -0,255; 0,066; -0,065; -0,038; 0,262; 0,103; -0,156; 0,756; 0,039; 0,075; -0,128; 0,280; -0,245; -0,286; -0,145; 0,089; -0,101; 0,383; -0,070; 0,012; 0,142; 0,419; -0,176; -0,196; -0,144; -0,096; 0,208; -0,519; -0,122; -0,130; 0,053; -0,159; 0,639; 0,053; -0,037; 0,261; -0,168; -0,094; -0,223; -0,064; 0,059; -0,315; 0,158; 0,068; 0,264; -0,166; 0,057; -0,293; -0,158; 0,235; -0,348; 0,218; 0,401; 0,114; -0,027; -0,512; 0,051; 0,238; -0,574; -0,082; -0,241; -0,092; -0,244; 0,124; 0,067; -0,035; 0,142; -0,491; 0,036; -0,028; 0,329; 0,270; 0,131; -0,169; 0,065; -0,172; 0,185; -0,084; -0,288; 0,615; -0,005; -0,180; -0,060; 0,355; -0,138; 0,081; -0,262]\par\smallskip
\end{footnotesize}

**3.2 Objetivo y subgrafo de entrenamiento.** Se predicen nuevas `[:RATED]` usuario→película. El subgrafo se acotó, según las NOTAS, a las películas con al menos 20 calificaciones (proyección Cypher `califLP`): **1.974 nodos** (671 usuarios y 1.303 películas) y **69.104 relaciones `[:RATED]`**. GDS informa 138.208, porque cada arista no dirigida cuenta dos veces.

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
