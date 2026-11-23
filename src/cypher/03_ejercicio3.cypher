// @paso 3.0a_limpiar_modelo
CALL gds.model.drop('modeloLP_drama', false) YIELD modelName
RETURN modelName AS modeloLiberado;

// @paso 3.0b_limpiar_pipeline
CALL gds.pipeline.drop('pipeLP_drama', false) YIELD pipelineName
RETURN pipelineName AS pipelineLiberado;

// @paso 3.0c_limpiar_califW
CALL gds.graph.drop('califW', false) YIELD graphName
RETURN graphName AS proyeccionLiberada;

// @paso 3.0d_limpiar_califLP
CALL gds.graph.drop('califLP', false) YIELD graphName
RETURN graphName AS proyeccionLiberada;

// @paso 3.0e_proyeccion_califW
// Misma proyección del Ej. 1 (Usuario–Película, ponderada por rating, UNDIRECTED).
CALL gds.graph.project(
  'califW',
  ['User', 'Movie'],
  {RATED: {orientation: 'UNDIRECTED', properties: 'rating'}},
  {readConcurrency: 1}  // carga con un solo hilo: ids internos estables => muestreo reproducible
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;

// ---------------------------------------------------------------------
// Ejercicio 3.1 — Embedding con node2vec
// ---------------------------------------------------------------------
// @paso 3.1_node2vec_5_nodos
// 5 nodos elegidos de forma determinista: la película ancla, la película más
// calificada que no es la ancla y los 3 usuarios con más calificaciones.
CALL () {
  MATCH (:Genre {name: 'Drama'})<-[:IN_GENRE]-(m:Movie)
  WITH m, COUNT { (m)<-[:RATED]-(:User) } AS c
  ORDER BY c DESC, m.title ASC
  LIMIT 1
  RETURN m AS ancla
}
CALL (ancla) {
  MATCH (m:Movie) WHERE m <> ancla
  WITH m, COUNT { (m)<-[:RATED]-(:User) } AS c
  ORDER BY c DESC, m.title ASC
  LIMIT 1
  RETURN m AS otraPelicula
}
CALL () {
  MATCH (u:User)
  WITH u, COUNT { (u)-[:RATED]->(:Movie) } AS c
  ORDER BY c DESC, u.name ASC
  LIMIT 3
  RETURN collect(u) AS usuarios
}
WITH [ancla, otraPelicula] + usuarios AS elegidos
CALL gds.node2vec.stream('califW', {
  embeddingDimension: 128,
  walkLength: 40,
  walksPerNode: 10,
  iterations: 1,
  relationshipWeightProperty: 'rating',
  randomSeed: 42,
  concurrency: 1
})
YIELD nodeId, embedding
WITH elegidos, gds.util.asNode(nodeId) AS n, embedding
WHERE n IN elegidos
RETURN labels(n)[0] AS tipo,
       coalesce(n.title, n.name) AS nodo,
       size(embedding) AS dimension,
       embedding
ORDER BY tipo ASC, nodo ASC;

// ---------------------------------------------------------------------
// Ejercicio 3.2 — Subgrafo de entrenamiento
// ---------------------------------------------------------------------
// @paso 3.2a_subgrafo_entrenamiento
// Proyección Cypher acotada (NOTAS) a las películas con >= 20 calificaciones.
MATCH (u:User)-[r:RATED]->(m:Movie)
WHERE COUNT { (m)<-[:RATED]-(:User) } >= 20
WITH gds.graph.project(
  'califLP', u, m,
  {
    sourceNodeLabels: 'User',
    targetNodeLabels: 'Movie',
    relationshipType: 'RATED',
    relationshipProperties: {rating: r.rating}
  },
  {undirectedRelationshipTypes: ['RATED']}
) AS g
RETURN g.graphName AS grafo, g.nodeCount AS nodeCount, g.relationshipCount AS relationshipCount;

// @paso 3.2b_subgrafo_conteo_en_la_base
// El mismo subgrafo contado en la base (las [:RATED] reales, sin duplicar por UNDIRECTED).
MATCH (u:User)-[r:RATED]->(m:Movie)
WHERE COUNT { (m)<-[:RATED]-(:User) } >= 20
RETURN count(DISTINCT u) AS usuarios,
       count(DISTINCT m) AS peliculas,
       count(DISTINCT u) + count(DISTINCT m) AS nodos,
       count(r) AS relacionesRated;

// ---------------------------------------------------------------------
// Ejercicio 3.3 — Pipeline de link prediction
// ---------------------------------------------------------------------
// @paso 3.3a_pipeline_crear
CALL gds.beta.pipeline.linkPrediction.create('pipeLP_drama') YIELD name
RETURN name AS pipeline;

// @paso 3.3b_pipeline_paso_node2vec
// node2vec como PASO del pipeline: GDS lo calcula sobre el grafo de entrenamiento
// (feature-input), así las aristas de test no se filtran al embedding.
CALL gds.beta.pipeline.linkPrediction.addNodeProperty('pipeLP_drama', 'node2vec', {
  mutateProperty: 'emb',
  embeddingDimension: 128,
  walkLength: 40,
  walksPerNode: 10,
  iterations: 1,
  relationshipWeightProperty: 'rating',
  randomSeed: 42,
  concurrency: 1
})
YIELD nodePropertySteps
RETURN size(nodePropertySteps) AS pasosDePropiedad;

// @paso 3.3c_pipeline_feature_hadamard
CALL gds.beta.pipeline.linkPrediction.addFeature('pipeLP_drama', 'hadamard', {nodeProperties: ['emb']})
YIELD featureSteps
RETURN featureSteps;

// @paso 3.3d_pipeline_split
CALL gds.beta.pipeline.linkPrediction.configureSplit('pipeLP_drama', {
  testFraction: 0.1,
  trainFraction: 0.1,
  validationFolds: 3,
  negativeSamplingRatio: 1.0
})
YIELD splitConfig
RETURN splitConfig;

// @paso 3.3e_modelo_lr_penalty_0
CALL gds.beta.pipeline.linkPrediction.addLogisticRegression('pipeLP_drama', {penalty: 0.0})
YIELD parameterSpace
RETURN size(parameterSpace.LogisticRegression) AS configuracionesLR;

// @paso 3.3f_modelo_lr_penalty_001
CALL gds.beta.pipeline.linkPrediction.addLogisticRegression('pipeLP_drama', {penalty: 0.01})
YIELD parameterSpace
RETURN size(parameterSpace.LogisticRegression) AS configuracionesLR;

// @paso 3.3g_modelo_lr_penalty_01
CALL gds.beta.pipeline.linkPrediction.addLogisticRegression('pipeLP_drama', {penalty: 0.1})
YIELD parameterSpace
RETURN size(parameterSpace.LogisticRegression) AS configuracionesLR;

// @paso 3.3h_modelo_rf_10_arboles
CALL gds.beta.pipeline.linkPrediction.addRandomForest('pipeLP_drama', {numberOfDecisionTrees: 10, maxDepth: 10})
YIELD parameterSpace
RETURN size(parameterSpace.RandomForest) AS configuracionesRF;

// @paso 3.3i_modelo_rf_25_arboles
CALL gds.beta.pipeline.linkPrediction.addRandomForest('pipeLP_drama', {numberOfDecisionTrees: 25, maxDepth: 15})
YIELD parameterSpace
RETURN size(parameterSpace.RandomForest) AS configuracionesRF;

// @paso 3.3j_entrenamiento
// Predice [:RATED] User→Movie. Métrica AUCPR (adecuada para el desbalance de clases).
CALL gds.beta.pipeline.linkPrediction.train('califLP', {
  pipeline: 'pipeLP_drama',
  modelName: 'modeloLP_drama',
  targetRelationshipType: 'RATED',
  sourceNodeLabel: 'User',
  targetNodeLabel: 'Movie',
  metrics: ['AUCPR'],
  randomSeed: 42
})
YIELD modelInfo, modelSelectionStats, trainMillis
RETURN modelInfo.bestParameters AS modeloGanador,
       modelInfo.metrics.AUCPR.test AS aucprTest,
       modelInfo.metrics.AUCPR.outerTrain AS aucprOuterTrain,
       modelInfo.metrics.AUCPR.validation AS aucprValidacion,
       modelInfo.metrics.AUCPR.train AS aucprTrain,
       modelSelectionStats,
       trainMillis;

// @paso 3.3k_prediccion_top5
// Los 5 pares usuario→película (todavía sin [:RATED]) con mayor probabilidad predicha.
// concurrency 1: el Random Forest devuelve la fracción de árboles que votan "sí", así que
// hay empates en 1.0; con un solo hilo la elección entre empatados es reproducible.
CALL gds.beta.pipeline.linkPrediction.predict.stream('califLP', {
  modelName: 'modeloLP_drama',
  topN: 5,
  concurrency: 1
})
YIELD node1, node2, probability
WITH gds.util.asNode(node1) AS a, gds.util.asNode(node2) AS b, probability
WITH CASE WHEN a:User THEN a ELSE b END AS u,
     CASE WHEN a:User THEN b ELSE a END AS m,
     probability
RETURN u.name AS usuario,
       m.title AS pelicula,
       m.year AS anio,
       probability AS probabilidad,
       EXISTS { (u)-[:RATED]->(m) } AS yaExisteEnLaBase
ORDER BY probabilidad DESC, usuario ASC, pelicula ASC;

// @paso 3.3l_empates_en_probabilidad_maxima
// Contexto del top 5: cuántos pares nuevos reciben probabilidad >= 0.999 (todos los árboles
// del Random Forest votan "sí"). Búsqueda exhaustiva con umbral.
CALL gds.beta.pipeline.linkPrediction.predict.stream('califLP', {
  modelName: 'modeloLP_drama',
  topN: 1000000,
  threshold: 0.999,
  concurrency: 1
})
YIELD node1, node2, probability
RETURN count(*) AS paresConProbabilidadMaxima,
       count(DISTINCT CASE WHEN gds.util.asNode(node1):User THEN node1 ELSE node2 END) AS usuariosDistintos;
