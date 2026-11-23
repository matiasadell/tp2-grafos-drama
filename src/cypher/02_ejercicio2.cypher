// @paso 2.0a_borrar_indice_del_dump
DROP INDEX index_fc5f831e IF EXISTS;

// @paso 2.0b_borrar_indice_propio
DROP INDEX movie_year_range IF EXISTS;

// @paso 2.0c_control_sin_indice_year
// Control: no debe quedar ningún índice sobre Movie(year).
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state
WHERE 'Movie' IN coalesce(labelsOrTypes, []) AND 'year' IN coalesce(properties, [])
RETURN count(*) AS indicesSobreMovieYear;

// @paso 2.0d_borrar_ratingNorm
// Se borra ratingNorm (lo escribe el 2.4) para que la verificación sea de esta corrida.
MATCH ()-[r:RATED]->() WHERE r.ratingNorm IS NOT NULL
CALL (r) { REMOVE r.ratingNorm } IN TRANSACTIONS OF 10000 ROWS;

// ---------------------------------------------------------------------
// Ejercicio 2.1 — PROFILE sin índice
// ---------------------------------------------------------------------
// @paso 2.1_profile_sin_indice medir=20
PROFILE
MATCH (m:Movie)
WHERE m.year >= 1990 AND m.year <= 1999
RETURN count(m) AS peliculas;

// ---------------------------------------------------------------------
// Ejercicio 2.2 — Índice de rango y nuevo PROFILE
// ---------------------------------------------------------------------
// @paso 2.2a_crear_indice_rango
CREATE RANGE INDEX movie_year_range IF NOT EXISTS FOR (m:Movie) ON (m.year);

// @paso 2.2b_esperar_indice
CALL db.awaitIndexes(300);

// @paso 2.2c_control_indice
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state, populationPercent
WHERE name = 'movie_year_range'
RETURN name, type, labelsOrTypes, properties, state, populationPercent;

// @paso 2.2_profile_con_indice medir=20
PROFILE
MATCH (m:Movie)
WHERE m.year >= 1990 AND m.year <= 1999
RETURN count(m) AS peliculas;

// ---------------------------------------------------------------------
// Ejercicio 2.3 — EXPLAIN, runtime y Eager
// ---------------------------------------------------------------------
// @paso 2.3a_explain_rango
EXPLAIN
MATCH (m:Movie)
WHERE m.year >= 1990 AND m.year <= 1999
RETURN count(m) AS peliculas;

// @paso 2.3b_profile_rango
PROFILE
MATCH (m:Movie)
WHERE m.year >= 1990 AND m.year <= 1999
RETURN count(m) AS peliculas;

// @paso 2.3c_explain_escritura_2_4
// Plan de la sentencia de escritura del 2.4 (sin ejecutarla), para buscar un operador Eager.
EXPLAIN
MATCH (u:User)
CALL (u) {
  MATCH (u)-[r:RATED]->(:Movie)
  WITH collect(r) AS calificaciones, avg(r.rating) AS promedio
  UNWIND calificaciones AS r
  SET r.ratingNorm = r.rating - promedio
} IN TRANSACTIONS OF 50 ROWS;

// ---------------------------------------------------------------------
// Ejercicio 2.4 — Escritura por lotes de ratingNorm
// ---------------------------------------------------------------------
// @paso 2.4a_escritura_ratingNorm
// Un lote = 50 usuarios (cada uno con todas sus calificaciones), así cada
// transacción calcula el promedio de su usuario y escribe sus [:RATED].
MATCH (u:User)
CALL (u) {
  MATCH (u)-[r:RATED]->(:Movie)
  WITH collect(r) AS calificaciones, avg(r.rating) AS promedio
  UNWIND calificaciones AS r
  SET r.ratingNorm = r.rating - promedio
} IN TRANSACTIONS OF 50 ROWS;

// @paso 2.4b_verificacion_cobertura
// Todas las [:RATED] tienen ratingNorm y el promedio global queda en ~0.
MATCH ()-[r:RATED]->()
RETURN count(r) AS totalRated,
       count(r.ratingNorm) AS conRatingNorm,
       round(avg(r.ratingNorm), 6) AS promedioGlobalRatingNorm,
       round(min(r.ratingNorm), 3) AS minimo,
       round(max(r.ratingNorm), 3) AS maximo;

// @paso 2.4c_verificacion_por_usuario
// Por usuario, el promedio de ratingNorm tiene que dar 0 (es rating centrado en su media).
MATCH (u:User)-[r:RATED]->()
WITH u, count(r) AS calificaciones, avg(r.rating) AS promedioRating, avg(r.ratingNorm) AS promedioRatingNorm
RETURN u.name AS usuario,
       calificaciones,
       round(promedioRating, 3) AS promedioRating,
       round(promedioRatingNorm, 6) AS promedioRatingNorm
ORDER BY calificaciones DESC, usuario ASC
LIMIT 5;

// @paso 2.4d_ejemplos_pelicula_ancla
// Ejemplos sobre la película ancla: misma nota, distinta ratingNorm según la media de cada usuario.
CALL () {
  MATCH (:Genre {name: 'Drama'})<-[:IN_GENRE]-(m:Movie)
  WITH m, COUNT { (m)<-[:RATED]-(:User) } AS c
  ORDER BY c DESC, m.title ASC
  LIMIT 1
  RETURN m AS ancla
}
MATCH (u:User)-[r:RATED]->(ancla)
RETURN ancla.title AS pelicula, u.name AS usuario, r.rating AS rating, round(r.ratingNorm, 3) AS ratingNorm
ORDER BY r.ratingNorm DESC, usuario ASC
LIMIT 5;
