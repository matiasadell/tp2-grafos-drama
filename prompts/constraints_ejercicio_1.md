# Constraints — Ejercicio 1

GDS: proyección y algoritmos.

- **1.1** Proyectar Usuario–Película desde `[:RATED]`, ponderado por `rating`, con el nombre **`califW`** (UNDIRECTED). Entregable: `nodeCount` y `relationshipCount`.
- **1.2** Betweenness con muestreo y **sin peso**: el peso actúa como costo/distancia, así que un rating alto "alejaría" a los nodos; se justifica en el informe. Entregable: top 10.
- **1.3** Label Propagation **ponderado** por rating. Entregable: cantidad de comunidades y tamaño de las 5 mayores.
- **1.4** KNN sobre un embedding de usuarios: **FastRP (dim 128, seed 42, ponderado)** sobre `califW`, solo para este punto; KNN filtrado a `:User`. Entregable: 10 pares más similares, sin autosimilitud, con su puntaje.
- **1.5** Betweenness en modos `stream`, `stats` y `write`. Entregable: la propiedad que persiste `write` y la captura de cada corrida.
