// ---------------------------------------------------------------------
// Común 1 — Panorama del grafo
// ---------------------------------------------------------------------
// @paso C.1a_nodos_por_etiqueta
// Panorama (1/4): nodos por etiqueta. Un nodo :Person:Actor cuenta en las dos.
MATCH (n)
UNWIND labels(n) AS etiqueta
RETURN etiqueta, count(*) AS nodos
ORDER BY nodos DESC, etiqueta ASC;

// @paso C.1b_nodos_por_combinacion
// Panorama (2/4): nodos por combinación exacta de etiquetas (suma = total de nodos).
MATCH (n)
RETURN labels(n) AS etiquetas, count(*) AS nodos
ORDER BY nodos DESC;

// @paso C.2_relaciones_por_tipo
// Panorama (3/4): relaciones por tipo.
MATCH ()-[r]->()
RETURN type(r) AS tipo, count(*) AS relaciones
ORDER BY relaciones DESC, tipo ASC;

// @paso C.3_totales
// Panorama (4/4): totales contra lo que dice la consigna (28.863 nodos y 166.261 relaciones).
MATCH (n)
WITH count(n) AS nodos
MATCH ()-[r]->()
WITH nodos, count(r) AS relaciones
RETURN nodos, relaciones, (nodos = 28863 AND relaciones = 166261) AS coincideConConsigna;

// @paso C.4_top3_mas_calificadas
// Las 3 películas con más calificaciones (desempate por título).
MATCH (m:Movie)<-[r:RATED]-(:User)
RETURN m.title AS pelicula, m.year AS anio, count(r) AS calificaciones
ORDER BY calificaciones DESC, pelicula ASC
LIMIT 3;

// ---------------------------------------------------------------------
// Común 2 — Recomendación base
// ---------------------------------------------------------------------
// @paso C.5_pelicula_ancla
// Película ancla del eje Drama.
MATCH (:Genre {name: 'Drama'})<-[:IN_GENRE]-(m:Movie)
WITH m, COUNT { (m)<-[:RATED]-(:User) } AS calificaciones
RETURN m.title AS peliculaAncla, m.year AS anio, calificaciones
ORDER BY calificaciones DESC, peliculaAncla ASC
LIMIT 1;

// @paso C.6_recomendacion_base
// Recomendación base (sin GDS): 10 películas para la ancla, con el patrón
// (:Movie)<-[:RATED]-(:User)-[:RATED]->(rec:Movie), ordenadas por usuarios en común.
CALL () {
  MATCH (:Genre {name: 'Drama'})<-[:IN_GENRE]-(m:Movie)
  WITH m, COUNT { (m)<-[:RATED]-(:User) } AS calificaciones
  ORDER BY calificaciones DESC, m.title ASC
  LIMIT 1
  RETURN m AS ancla
}
MATCH (ancla)<-[:RATED]-(u:User)-[:RATED]->(rec:Movie)
WHERE rec <> ancla
RETURN ancla.title AS peliculaAncla,
       rec.title AS recomendacion,
       rec.year AS anio,
       count(DISTINCT u) AS usuariosEnComun
ORDER BY usuariosEnComun DESC, recomendacion ASC
LIMIT 10;
