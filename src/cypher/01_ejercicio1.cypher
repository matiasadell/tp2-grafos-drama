// @paso 1.0a_limpiar_proyeccion
CALL gds.graph.drop('califW', false) YIELD graphName
RETURN graphName AS proyeccionLiberada;

// @paso 1.0b_limpiar_propiedad_betweenness
// La propiedad escrita por el modo write (1.5) se borra para que la corrida sea reproducible.
MATCH (n) WHERE n.betweenness IS NOT NULL
REMOVE n.betweenness
RETURN count(n) AS propiedadesBorradas;

// ---------------------------------------------------------------------
// Ejercicio 1.1 — Proyección a memoria
// ---------------------------------------------------------------------
// @paso 1.1_proyeccion_califW
// UNDIRECTED (indicación de la cátedra): GDS guarda cada relación en los dos
// sentidos, así que relationshipCount es el doble de las [:RATED] de la base.
CALL gds.graph.project(
  'califW',
  ['User', 'Movie'],
  {RATED: {orientation: 'UNDIRECTED', properties: 'rating'}},
  {readConcurrency: 1}  // carga con un solo hilo: ids internos estables => muestreo reproducible
)
YIELD graphName, nodeCount, relationshipCount, projectMillis
RETURN graphName, nodeCount, relationshipCount, projectMillis;

// ---------------------------------------------------------------------
// Ejercicio 1.2 — Cálculo de betweenness
// ---------------------------------------------------------------------
// @paso 1.2_betweenness_top10
CALL gds.betweenness.stream('califW', {samplingSize: 1000, samplingSeed: 42, concurrency: 1})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS n, score
RETURN labels(n)[0] AS tipo,
       coalesce(n.title, n.name) AS nodo,
       score AS betweenness
ORDER BY betweenness DESC, nodo ASC
LIMIT 10;

// ---------------------------------------------------------------------
// Ejercicio 1.3 — Comunidades con Label Propagation
// ---------------------------------------------------------------------
// @paso 1.3a_lpa_stats
// concurrency 1: LPA no acepta semilla y, con un solo hilo, el resultado es reproducible.
CALL gds.labelPropagation.stats('califW', {relationshipWeightProperty: 'rating', concurrency: 1})
YIELD communityCount, ranIterations, didConverge, communityDistribution
RETURN communityCount, ranIterations, didConverge, communityDistribution;

// @paso 1.3b_lpa_top5_comunidades
CALL gds.labelPropagation.stream('califW', {relationshipWeightProperty: 'rating', concurrency: 1})
YIELD nodeId, communityId
WITH communityId, gds.util.asNode(nodeId) AS n
WITH communityId,
     count(*) AS tamanio,
     count(CASE WHEN n:User THEN 1 END) AS usuarios,
     count(CASE WHEN n:Movie THEN 1 END) AS peliculas
ORDER BY tamanio DESC, communityId ASC
WITH collect({id: communityId, tamanio: tamanio, usuarios: usuarios, peliculas: peliculas}) AS comunidades
UNWIND range(0, size(comunidades[0..5]) - 1) AS i
RETURN size(comunidades) AS totalComunidades,
       i + 1 AS puesto,
       comunidades[i].id AS comunidadId,
       comunidades[i].tamanio AS tamanio,
       comunidades[i].usuarios AS usuarios,
       comunidades[i].peliculas AS peliculas
ORDER BY puesto;

// ---------------------------------------------------------------------
// Ejercicio 1.4 — KNN sobre embedding de usuarios
// ---------------------------------------------------------------------
// @paso 1.4a_fastrp_embedding_usuarios
// Embedding FastRP (dim 128, semilla 42, ponderado por rating) agregado a la proyección (mutate).
CALL gds.fastRP.mutate('califW', {
  embeddingDimension: 128,
  randomSeed: 42,
  relationshipWeightProperty: 'rating',
  mutateProperty: 'embFastRP'
})
YIELD nodePropertiesWritten, computeMillis
RETURN nodePropertiesWritten, computeMillis;

// @paso 1.4b_knn_usuarios_top10
// KNN solo entre :User (similitud coseno del embedding). Las listas de KNN no son
// simétricas: el par se normaliza (a<b) y se deduplica, sin autosimilitud.
CALL gds.knn.stream('califW', {
  nodeLabels: ['User'],
  nodeProperties: ['embFastRP'],
  topK: 10,
  randomSeed: 42,
  concurrency: 1,
  sampleRate: 1.0,
  deltaThreshold: 0.0
})
YIELD node1, node2, similarity
WITH CASE WHEN node1 < node2 THEN node1 ELSE node2 END AS a,
     CASE WHEN node1 < node2 THEN node2 ELSE node1 END AS b,
     similarity
WHERE a <> b
WITH DISTINCT a, b, similarity
RETURN gds.util.asNode(a).name AS usuario1,
       gds.util.asNode(b).name AS usuario2,
       similarity AS similitud
ORDER BY similitud DESC, usuario1 ASC, usuario2 ASC
LIMIT 10;

// ---------------------------------------------------------------------
// Ejercicio 1.5 — Betweenness en stream, stats y write
// ---------------------------------------------------------------------
// @paso 1.5a_betweenness_stream
CALL gds.betweenness.stream('califW', {samplingSize: 1000, samplingSeed: 42, concurrency: 1})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS n, score
RETURN labels(n)[0] AS tipo,
       coalesce(n.title, n.name) AS nodo,
       score AS betweenness
ORDER BY betweenness DESC, nodo ASC
LIMIT 10;

// @paso 1.5b_betweenness_stats
CALL gds.betweenness.stats('califW', {samplingSize: 1000, samplingSeed: 42, concurrency: 1})
YIELD centralityDistribution, preProcessingMillis, computeMillis, postProcessingMillis
RETURN centralityDistribution, preProcessingMillis, computeMillis, postProcessingMillis;

// @paso 1.5c_betweenness_write
// Persiste el puntaje en la base como propiedad de nodo 'betweenness'.
CALL gds.betweenness.write('califW', {samplingSize: 1000, samplingSeed: 42, concurrency: 1, writeProperty: 'betweenness'})
YIELD nodePropertiesWritten, centralityDistribution, computeMillis, writeMillis
RETURN 'betweenness' AS propiedadEscrita, nodePropertiesWritten, computeMillis, writeMillis, centralityDistribution;

// @paso 1.5d_verificacion_write
// Verificación: la propiedad quedó en la base y su top 5 coincide con el modo stream.
MATCH (n) WHERE n.betweenness IS NOT NULL
WITH n ORDER BY n.betweenness DESC, coalesce(n.title, n.name) ASC
WITH count(n) AS nodosConPropiedad, collect(coalesce(n.title, n.name) + ' (' + toString(round(n.betweenness, 1)) + ')')[0..5] AS top5DesdeLaBase
RETURN nodosConPropiedad, top5DesdeLaBase;
