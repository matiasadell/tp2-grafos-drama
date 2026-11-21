# Capturas de Query (las saca el grupo)

Guardar acá, en PNG y con estos nombres exactos (ver `docs/checklist_capturas.md`):

| Archivo | Contenido |
|---|---|
| `2.1_profile_sin_indice.png` | PROFILE del rango 1990–1999 sin índice sobre `Movie.year` |
| `2.2_profile_con_indice.png` | El mismo PROFILE con `movie_year_range` (NodeIndexSeekByRange) |
| `2.3a_explain_rango.png` | EXPLAIN de la consulta de rango |
| `2.3b_profile_rango.png` | PROFILE de la consulta de rango (con el runtime visible) |
| `2.3c_explain_escritura_2_4.png` | EXPLAIN de la escritura por lotes del 2.4 (¿Eager?) |
| `1.5a_betweenness_stream.png` | Betweenness, modo stream |
| `1.5b_betweenness_stats.png` | Betweenness, modo stats |
| `1.5c_betweenness_write.png` | Betweenness, modo write |
| `2.4_verificacion.png` | (opcional) Verificación de `ratingNorm` |

Si una captura no entra en una pantalla, se puede partir en `<nombre>_a.png` y `<nombre>_b.png`.
