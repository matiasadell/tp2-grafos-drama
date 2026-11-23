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
- **Película ancla.** La película de Drama con más `[:RATED]` es **{{valor:00_parte_comun/C.5_pelicula_ancla;col=peliculaAncla}} ({{valor:00_parte_comun/C.5_pelicula_ancla;col=anio;crudo=1}})**, con {{valor:00_parte_comun/C.5_pelicula_ancla;col=calificaciones}} calificaciones. Se recalcula dentro de cada consulta; no está escrita a mano.

## Parte común — síntesis

**Panorama.** El grafo tiene **{{valor:00_parte_comun/C.3_totales;col=nodos}} nodos y {{valor:00_parte_comun/C.3_totales;col=relaciones}} relaciones**, que coinciden con la consigna: {{valor:00_parte_comun/C.3_totales;col=coincideConConsigna}}. Una `:Person` puede ser `:Actor` y `:Director` a la vez (487 lo son), por eso las etiquetas suman más que el total.

{{tabla:00_parte_comun/C.1a_nodos_por_etiqueta;cols=etiqueta,nodos;titulos=Etiqueta,Nodos}}

{{tabla:00_parte_comun/C.2_relaciones_por_tipo;cols=tipo,relaciones;titulos=Tipo de relación,Relaciones}}

**Las 3 películas con más calificaciones:**

{{tabla:00_parte_comun/C.4_top3_mas_calificadas;cols=pelicula,anio,calificaciones;titulos=Película,Año,Calificaciones;crudas=anio}}

**Recomendación base (sin GDS) para la ancla.** Se usa el patrón `(:Movie)<-[:RATED]-(:User)-[:RATED]->(rec:Movie)`, ordenado por usuarios en común:

{{tabla:00_parte_comun/C.6_recomendacion_base;cols=recomendacion,anio,usuariosEnComun;titulos=Recomendación,Año,Usuarios en común;crudas=anio}}

Es un filtrado colaborativo por co-ocurrencia: favorece los títulos muy populares de los noventa, que comparten público con *Forrest Gump*. No normaliza por popularidad.

## Ejercicio 1 — Graph Data Science sobre `califW`

**1.1 Proyección.** Se proyectó Usuario–Película desde `[:RATED]`, UNDIRECTED y con la propiedad `rating` como peso: **`califW` = {{valor:01_ejercicio1/1.1_proyeccion_califW;col=nodeCount}} nodos y {{valor:01_ejercicio1/1.1_proyeccion_califW;col=relationshipCount}} relaciones**. Son 671 usuarios y 9.125 películas. El conteo de relaciones duplica las 100.004 `[:RATED]` porque cada arista no dirigida se guarda en ambos sentidos.

**1.2 Intermediación (betweenness).** Se usó muestreo (`samplingSize` 1000, `samplingSeed` 42, `concurrency` 1) y **sin peso**. GDS interpreta el peso como *costo* del camino, así que usar el rating haría que una calificación alta "alejara" a usuario y película, al revés de lo que significa. El top 10 se ve en la Figura 1 (punto 1.5, modo stream), que usa esta misma consulta.

Los diez son usuarios, y coinciden con los más activos: *Darlene Garcia* tiene 2.391 calificaciones y *Robert Brooks*, 1.868. En un grafo bipartito, los caminos entre películas pasan por usuarios; los que calificaron mucho, incluidos títulos poco vistos, son los puentes obligados. Con muestreo los valores son una aproximación. Con varios hilos, la selección de nodos fuente variaba entre corridas a pesar de la semilla (hasta un 2 %); con `concurrency` 1 el resultado es idéntico en cada corrida.

**1.3 Label Propagation (ponderado por rating).** Hay **{{valor:01_ejercicio1/1.3a_lpa_stats;col=communityCount}} comunidades**. El algoritmo convergió en {{valor:01_ejercicio1/1.3a_lpa_stats;col=ranIterations}} iteraciones, con `concurrency` 1 para que sea reproducible. Las 5 mayores:

{{tabla:01_ejercicio1/1.3b_lpa_top5_comunidades;cols=puesto,comunidadId,tamanio,usuarios,peliculas;titulos=Puesto,Comunidad,Tamaño,Usuarios,Películas;crudas=comunidadId}}

El resultado es casi trivial: una comunidad gigante con los 671 usuarios y 9.066 películas, más 59 *singletons*, que son exactamente las 59 películas que nadie calificó y quedan aisladas en la proyección. El grafo de calificaciones es una única componente muy densa (unas 149 calificaciones por usuario). Los pesos son todos positivos (de 0,5 a 5), así que solo modulan la votación y LPA converge a la etiqueta dominante. Para este grafo, LPA no encuentra estructura de comunidades.

**1.4 KNN sobre un embedding de usuarios.** El embedding es **FastRP** (dimensión 128, semilla 42, ponderado por rating), agregado a `califW` con `mutate`. KNN se corrió solo sobre `:User` (coseno, `topK` 10, semilla 42 y `concurrency` 1). Los pares se normalizaron y se deduplicaron, sin autosimilitud:

{{tabla:01_ejercicio1/1.4b_knn_usuarios_top10;cols=usuario1,usuario2,similitud;titulos=Usuario 1,Usuario 2,Similitud;dec=4}}

Las similitudes son muy altas (cerca de 0,997). FastRP promedia vecindarios y, en un grafo tan denso, los embeddings de los usuarios quedan concentrados. El ranking sirve igual para ordenar perfiles cercanos (*Aaron Nelson* aparece como "centro" de varios pares).

**1.5 Betweenness en los modos stream, stats y write.** Se usaron los mismos parámetros que en el 1.2. El modo **write persiste la propiedad de nodo `betweenness`** en {{valor:01_ejercicio1/1.5c_betweenness_write;col=nodePropertiesWritten}} nodos. La verificación en la base coincide con el top del modo stream.

{{captura:1.5a_betweenness_stream;ancho=0.85;titulo=1.5 — modo stream|01_ejercicio1/1.5a_betweenness_stream;cols=tipo,nodo,betweenness;titulos=Tipo,Nodo,Betweenness (stream);dec=0;n=5}}

{{captura:1.5b_betweenness_stats;ancho=0.85;titulo=1.5 — modo stats|01_ejercicio1/1.5b_betweenness_stats;cols=centralityDistribution,computeMillis;titulos=Distribución (stats),computeMillis;claves=min,mean,p50,p99,max;dec=1}}

{{captura:1.5c_betweenness_write;ancho=0.85;titulo=1.5 — modo write|01_ejercicio1/1.5c_betweenness_write;cols=propiedadEscrita,nodePropertiesWritten,computeMillis,writeMillis;titulos=Propiedad escrita,nodePropertiesWritten,computeMillis,writeMillis}}

## Ejercicio 2 — Índices, planes y escritura por lotes

La consulta es `MATCH (m:Movie) WHERE m.year >= 1990 AND m.year <= 1999 RETURN count(m)`, que devuelve {{valor:02_ejercicio2/2.1_profile_sin_indice;col=peliculas}} películas. **El dump ya trae un índice RANGE sobre `Movie(year)`** (`index_fc5f831e`). Para medir "sin el índice específico", el script primero lo borra y controla que no quede ninguno sobre `year`. Los tiempos son la mediana de 20 corridas después de un calentamiento.

**2.1 Sin índice.** El operador inicial es **{{json:02_ejercicio2/2.1_profile_sin_indice;ruta=plan_resumen.operador_inicial}}** (recorre las 9.125 `:Movie`), seguido de `Filter`: **{{json:02_ejercicio2/2.1_profile_sin_indice;ruta=plan_resumen.db_hits_total}} db hits**, {{json:02_ejercicio2/2.1_profile_sin_indice;ruta=medicion.mediana_ms;dec=1}} ms de punta a punta y {{json:02_ejercicio2/2.1_profile_sin_indice;ruta=medicion.mediana_operadores_ms;dec=2}} ms de operadores.

{{plan:2.1_profile_sin_indice;ancho=0.95;titulo=2.1 — PROFILE sin índice}}

**2.2 Con índice de rango `movie_year_range`.** El plan pasa a **{{json:02_ejercicio2/2.2_profile_con_indice;ruta=plan_resumen.operador_inicial}}**, que lee solo las entradas del rango: **{{json:02_ejercicio2/2.2_profile_con_indice;ruta=plan_resumen.db_hits_total}} db hits**, {{json:02_ejercicio2/2.2_profile_con_indice;ruta=medicion.mediana_ms;dec=1}} ms de punta a punta y {{json:02_ejercicio2/2.2_profile_con_indice;ruta=medicion.mediana_operadores_ms;dec=2}} ms de operadores.

{{plan:2.2_profile_con_indice;ancho=0.95;titulo=2.2 — PROFILE con índice de rango}}

| Factor de mejora (sin índice / con índice) | Valor |
|---|---|
| db hits | **{{cociente:02_ejercicio2/2.1_profile_sin_indice;02_ejercicio2/2.2_profile_con_indice;ruta=plan_resumen.db_hits_total;dec=1}}×** |
| Tiempo de operadores (PROFILE) | **{{cociente:02_ejercicio2/2.1_profile_sin_indice;02_ejercicio2/2.2_profile_con_indice;ruta=medicion.mediana_operadores_ms;dec=1}}×** |
| Tiempo de punta a punta (cliente) | {{cociente:02_ejercicio2/2.1_profile_sin_indice;02_ejercicio2/2.2_profile_con_indice;ruta=medicion.mediana_ms;dec=1}}× |

La mejora en el motor (db hits y tiempo de operadores) es de casi un orden de magnitud. De punta a punta es menor porque, con solo 9.125 películas, pesa el costo fijo del ida y vuelta con el servidor.

**2.3 EXPLAIN, runtime y Eager.** `EXPLAIN` muestra el plan estimado sin ejecutar (sin filas ni db hits reales). `PROFILE` confirma el **runtime {{json:02_ejercicio2/2.3b_profile_rango;ruta=plan_resumen.runtime}}** (planner COST, Cypher 25). En la consulta de rango **no aparece Eager**, como se esperaba en una lectura pura. Se analizó también la sentencia de escritura del 2.4: su plan (`TransactionForeach` → `Expand` → `EagerAggregation` → `Unwind` → `SetProperty`) **tampoco tiene un operador Eager**, porque lee `rating` y escribe otra propiedad, `ratingNorm`, así que no hay conflicto de lectura y escritura. `EagerAggregation` es la agregación que calcula el promedio, no la barrera Eager.

{{plan:2.3a_explain_rango;ancho=0.85;titulo=2.3 — EXPLAIN de la consulta de rango}}

{{plan:2.3b_profile_rango;ancho=0.85;titulo=2.3 — PROFILE de la consulta de rango (runtime)}}

{{plan:2.3c_explain_escritura_2_4;ancho=0.95;titulo=2.3 — EXPLAIN de la escritura del 2.4}}

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

{{tabla:02_ejercicio2/2.4b_verificacion_cobertura;cols=totalRated,conRatingNorm,promedioGlobalRatingNorm,minimo,maximo;titulos=RATED,Con ratingNorm,Promedio global,Mínimo,Máximo}}

{{tabla:02_ejercicio2/2.4c_verificacion_por_usuario;cols=usuario,calificaciones,promedioRating,promedioRatingNorm;titulos=Usuario,Calificaciones,Promedio rating,Promedio ratingNorm}}

## Ejercicio 3 — Embeddings, predicción de enlaces y PairRE

**3.1 node2vec sobre `califW`.** Configuración: dimensión 128, `walkLength` 40, `walksPerNode` 10, una iteración, caminatas sesgadas por el peso `rating`, semilla 42 y `concurrency` 1. Se muestran 5 nodos (la ancla, la película más calificada que no es la ancla y los 3 usuarios más activos). Cada vector tiene **{{valor:03_ejercicio3/3.1_node2vec_5_nodos;col=dimension}} componentes** y se referencia con una variable $\mathbf{v}_i$; debajo de la tabla están los vectores completos (3 decimales):

{{tabla:03_ejercicio3/3.1_node2vec_5_nodos;cols=tipo,nodo,dimension;titulos=Tipo,Nodo,Dimensión;var=v;vartitulo=Vector}}

{{vectores:03_ejercicio3/3.1_node2vec_5_nodos;col=embedding;etiqueta=nodo;var=v;dec=3}}

**3.2 Objetivo y subgrafo de entrenamiento.** Se predicen nuevas `[:RATED]` usuario→película. El subgrafo se acotó, según las NOTAS, a las películas con al menos 20 calificaciones (proyección Cypher `califLP`): **{{valor:03_ejercicio3/3.2a_subgrafo_entrenamiento;col=nodeCount}} nodos** ({{valor:03_ejercicio3/3.2b_subgrafo_conteo_en_la_base;col=usuarios}} usuarios y {{valor:03_ejercicio3/3.2b_subgrafo_conteo_en_la_base;col=peliculas}} películas) y **{{valor:03_ejercicio3/3.2b_subgrafo_conteo_en_la_base;col=relacionesRated}} relaciones `[:RATED]`**. GDS informa {{valor:03_ejercicio3/3.2a_subgrafo_entrenamiento;col=relationshipCount}}, porque cada arista no dirigida cuenta dos veces.

**3.3 Pipeline de link prediction.** node2vec es un **paso del pipeline** (`addNodeProperty`): GDS lo recalcula sobre el grafo de entrenamiento, así que las aristas de test no se filtran al embedding. La feature es el producto de Hadamard de los embeddings. Split: 10 % test, 10 % train del resto y 3 folds de validación, con muestreo negativo 1:1. Candidatos: regresión logística (`penalty` 0, 0,01 y 0,1) y Random Forest (10 árboles con profundidad 10, y 25 con profundidad 15). Métrica: AUCPR.

| Modelo candidato | AUCPR validación (media de 3 folds) |
|---|---|
| Regresión logística, `penalty` 0 / 0,01 / 0,1 | {{valor:03_ejercicio3/3.3j_entrenamiento;col=modelSelectionStats;ruta=modelCandidates.0.metrics.AUCPR.validation.avg;dec=3}} / {{valor:03_ejercicio3/3.3j_entrenamiento;col=modelSelectionStats;ruta=modelCandidates.1.metrics.AUCPR.validation.avg;dec=3}} / {{valor:03_ejercicio3/3.3j_entrenamiento;col=modelSelectionStats;ruta=modelCandidates.2.metrics.AUCPR.validation.avg;dec=3}} |
| Random Forest, 10 árboles y profundidad 10 | {{valor:03_ejercicio3/3.3j_entrenamiento;col=modelSelectionStats;ruta=modelCandidates.3.metrics.AUCPR.validation.avg;dec=3}} |
| **Random Forest, 25 árboles y profundidad 15 (ganador)** | **{{valor:03_ejercicio3/3.3j_entrenamiento;col=aucprValidacion;ruta=avg;dec=3}}** |

**AUCPR de test = {{valor:03_ejercicio3/3.3j_entrenamiento;col=aucprTest;dec=3}}** (en *outer-train*: {{valor:03_ejercicio3/3.3j_entrenamiento;col=aucprOuterTrain;dec=3}}). Con un negativo por cada positivo, un clasificador al azar daría ≈0,5. La regresión logística no logra separar bien el producto de Hadamard (≈0,68); el bosque captura interacciones entre componentes y gana con margen, aunque la brecha entre train y test muestra algo de sobreajuste. El Random Forest devuelve la fracción de árboles que votan "sí": **{{valor:03_ejercicio3/3.3l_empates_en_probabilidad_maxima;col=paresConProbabilidadMaxima}} pares nuevos** (de {{valor:03_ejercicio3/3.3l_empates_en_probabilidad_maxima;col=usuariosDistintos}} usuarios) empatan con probabilidad ≥ 0,999. El top 5, obtenido con `concurrency` 1 para que sea reproducible, es una selección entre esos empatados. Ninguno de los pares existe en la base:

{{tabla:03_ejercicio3/3.3k_prediccion_top5;cols=usuario,pelicula,anio,probabilidad,yaExisteEnLaBase;titulos=Usuario,Película,Año,Probabilidad,¿Ya existe?;dec=4;crudas=anio}}

**3.4 Completado de KG con PairRE** (notebook `ej3_4_pairre.ipynb`). Se usaron las tripletas `IN_GENRE` y `ACTED_IN` de las películas con al menos 20 calificaciones: {{json:../kg/pairre_metricas;ruta=tripletas.total}} tripletas y {{json:../kg/pairre_metricas;ruta=entidades}} entidades, con split 80/10/10 y semilla 42. PairRE se entrenó con dimensión 128 y 100 épocas, en CPU. En test filtrado: **MRR = {{json:../kg/pairre_metricas;ruta=mrr;dec=3}}** y **Hits@10 = {{json:../kg/pairre_metricas;ruta=hits_at_10;dec=3}}**. Hechos propuestos, `(película, IN_GENRE, Drama)`, entre películas que hoy no son Drama:

{{tabla:../kg/hechos_propuestos;cols=pelicula,genero,score,generos_actuales;titulos=Película,Género propuesto,Score,Géneros actuales;dec=3}}

Un ranking al azar daría Hits@10 ≈ 10/4.052 ≈ 0,0025, así que el modelo es unas 75 veces mejor. Igual, el valor queda lejos del dataset *Nations* de la práctica (MRR ≈ 0,73) porque este KG es **ralo**: unas 2,2 tripletas por entidad, y la mayoría de los actores aparece una o dos veces. La pérdida converge hacia la época 20. Los tres hechos propuestos son plausibles: *Vanilla Sky* suele describirse como drama psicológico, *The African Queen* como aventura romántica con mucho de drama, y *Devil in a Blue Dress* como drama criminal neo-noir. Se verificó contra Neo4j que hoy ninguna de las tres tiene el género Drama. El score de PairRE es una distancia con signo negativo: más alto es más plausible.
