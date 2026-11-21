# Context — Consigna

- `CONSIGNA.md` transcribe el Trabajo 2 y las secciones comunes. La fuente original es `context/TP_2-2.pdf`, que trae 7 trabajos; a este grupo solo le aplican el Trabajo 2 y las secciones comunes.
- **Esquema del grafo:**
  - Nodos: `(:Movie {title, year, plot, imdbRating})`, `(:Person {name})` (puede tener también `:Actor`/`:Director`), `(:Genre {name})`, `(:User {name})`.
  - Relaciones: `ACTED_IN`, `DIRECTED` (Person→Movie), `IN_GENRE` (Movie→Genre) y `RATED {rating, timestamp}` (User→Movie).
  - Los géneros son los de MovieLens, en inglés.
- **Película ancla:** la película del género «Drama» con más `[:RATED]` (se desempata por título). Se usa donde la consigna la pida.
