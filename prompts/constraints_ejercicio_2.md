# Constraints — Ejercicio 2

Índices, planes de ejecución y escritura por lotes.

- **2.1** PROFILE **sin el índice específico** de una consulta de rango de años (1990–1999). Entregable: operador inicial, db hits y tiempo.
- **2.2** Índice de **RANGO sobre `Movie.year`** y la misma consulta con PROFILE. Entregable: plan con el seek por índice, db hits, tiempo y factor de mejora.
- **2.3** EXPLAIN y PROFILE de la consulta de rango (runtime; sin Eager) **y de la escritura del 2.4** (donde puede aparecer Eager). Entregable: el runtime (pipelined o slotted) y el paso en que está el operador Eager, si aparece.
- **2.4** Agregar a cada `[:RATED]` la propiedad **`ratingNorm`** = rating − promedio de ese usuario, con `CALL { … } IN TRANSACTIONS`. Entregable: la sentencia y la consulta de verificación con su resultado.
