# Checklist de capturas en Query (para el grupo)

Las Indicaciones de la consigna piden los planes PROFILE/EXPLAIN **como captura de Query**. También el punto 1.5 pide "la captura de cada corrida". Esta guía dice exactamente qué correr, en qué orden y con qué nombre guardar cada imagen.

- **Dónde guardar:** en `outputs/capturas/`, en PNG, con el **nombre exacto** de la tabla. `src/tp2/build_informe.py` las busca por nombre. Si falta alguna, el informe usa el render de respaldo de `outputs/planes/` y lo marca como tal.
- **Antes de empezar:**
  - el DBMS `tp2-recommendations` tiene que estar iniciado; abrí **Query** desde Neo4j Desktop;
  - corré cada consulta **de a una**: seleccioná solo ese bloque y ejecutalo;
  - en los PROFILE, ejecutá la consulta **dos veces** y capturá la segunda, con la caché caliente, que es como mide el runner.
- **Qué tiene que verse:** el plan completo (vista de plan, con los operadores expandidos), los **db hits** y las **filas** por operador, el **tiempo total** y el **runtime**. Query muestra el runtime en el resumen del plan (por ejemplo, `Runtime PIPELINED`). Si no entra en una pantalla, hacé dos capturas: `_a` y `_b`.

---

## A. Ejercicio 2 (en este orden: el estado del índice importa)

Las consultas son las de `src/cypher/02_ejercicio2.cypher`.

| # | Ejecutar en Query | Guardar como |
|---|---|---|
| A1 | Preparación (no se captura):<br>`DROP INDEX index_fc5f831e IF EXISTS;`<br>`DROP INDEX movie_year_range IF EXISTS;` | — |
| A2 | **2.1 sin índice:**<br>`PROFILE MATCH (m:Movie) WHERE m.year >= 1990 AND m.year <= 1999 RETURN count(m) AS peliculas;` | `2.1_profile_sin_indice.png` |
| A3 | Crear el índice (no se captura):<br>`CREATE RANGE INDEX movie_year_range IF NOT EXISTS FOR (m:Movie) ON (m.year);`<br>`CALL db.awaitIndexes(300);` | — |
| A4 | **2.2 con índice:** la misma consulta del A2 (tiene que aparecer `NodeIndexSeekByRange`). | `2.2_profile_con_indice.png` |
| A5 | **2.3 EXPLAIN:**<br>`EXPLAIN MATCH (m:Movie) WHERE m.year >= 1990 AND m.year <= 1999 RETURN count(m) AS peliculas;` | `2.3a_explain_rango.png` |
| A6 | **2.3 PROFILE (runtime):** la misma consulta con `PROFILE`. En la imagen tiene que leerse el runtime. | `2.3b_profile_rango.png` |
| A7 | **2.3 escritura del 2.4 (buscar Eager):** el bloque `EXPLAIN MATCH (u:User) CALL (u) { … } IN TRANSACTIONS OF 50 ROWS;` del paso `2.3c_explain_escritura_2_4`. | `2.3c_explain_escritura_2_4.png` |
| A8 | **2.4** (opcional): la sentencia `2.4a_escritura_ratingNorm` y luego `2.4b_verificacion_cobertura`. Va como tabla en el informe; la captura es un extra. | `2.4_verificacion.png` (opcional) |

## B. Ejercicio 1, punto 1.5 (betweenness en los tres modos)

Las consultas son las de `src/cypher/01_ejercicio1.cypher`. Primero hay que tener la proyección en memoria.

| # | Ejecutar en Query | Guardar como |
|---|---|---|
| B1 | Preparación (no se captura): los pasos `1.0a_limpiar_proyeccion`, `1.0b_limpiar_propiedad_betweenness` y `1.1_proyeccion_califW`. | — |
| B2 | **Modo stream:** el paso `1.5a_betweenness_stream`. | `1.5a_betweenness_stream.png` |
| B3 | **Modo stats:** el paso `1.5b_betweenness_stats`. | `1.5b_betweenness_stats.png` |
| B4 | **Modo write:** el paso `1.5c_betweenness_write` (se tiene que ver `propiedadEscrita = betweenness` y `nodePropertiesWritten`). | `1.5c_betweenness_write.png` |

---

## Al terminar

1. Revisá que `outputs/capturas/` tenga las 8 imágenes obligatorias: A2, A4, A5, A6, A7, B2, B3 y B4.
2. Avisale a Claude ("las capturas están listas") para que regenere el informe y el zip (Task 14).
