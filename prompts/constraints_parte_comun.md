# Constraints — Parte común

- **Panorama:** nodos por etiqueta y relaciones por tipo (verificar 28.863 y 166.261) y las 3 películas con más calificaciones.
- **Recomendación base (sin GDS):** 10 películas para la ancla con `(:Movie)<-[:RATED]-(:User)-[:RATED]->(rec:Movie)`, ordenadas por usuarios en común.
