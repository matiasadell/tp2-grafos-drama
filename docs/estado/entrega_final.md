# Estado — Entrega final (Task 14)

Fecha: 2026-11-23. Cierre en el EVA: 23/11/2026, 23:59.

## Capturas

Facundo Mazzola subió las capturas en el commit `e8eac3a`. Están recortadas en `outputs/capturas/` y sin recortar en `outputs/capturas_originales/`. Las 8 obligatorias son **reales**, sacadas de Query, y ninguna usa el render de respaldo:

| Captura | Origen en el PDF |
|---|---|
| `1.5a_betweenness_stream` | captura (Figura 1) |
| `1.5b_betweenness_stats` | captura (Figura 2) |
| `1.5c_betweenness_write` | captura (Figura 3) |
| `2.1_profile_sin_indice` | captura (Figura 4) |
| `2.2_profile_con_indice` | captura (Figura 5) |
| `2.3a_explain_rango` | captura (Figura 6) |
| `2.3b_profile_rango` | captura (Figura 7) |
| `2.3c_explain_escritura_2_4` | captura (Figura 8) |

Los valores de las capturas coinciden con la evidencia del runner. Por ejemplo, en el 1.5 stream *Robert Brooks* tiene 905.486,79 y *Crystal Spencer* queda décima, como en el CSV con `concurrency: 1`. En el 2.2 aparece `movie_year_range` como índice usado.

## Revisión de la consigna, las queries y el informe (23/11)

- **Consigna:** `CONSIGNA.md` coincide con el Trabajo 2 de `context/TP_2-2.pdf`, tanto en los ejercicios como en las notas, las indicaciones y la entrega.
- **Queries:** cubren los 13 puntos y los dos de la parte común. Cumplen las indicaciones: semilla 42, proyecciones UNDIRECTED, los nombres `califW` y `ratingNorm`, y cada script libera lo que crea.
- **Informe:** correcciones sobre el build del commit `e8eac3a`:
  1. Al pasar `-H cabecera.tex`, pandoc ignora el `header-includes` del YAML, así que se perdían `float` y `[H]` y las figuras salían de lugar (la Figura 5 antes del texto del 2.2, la 8 en el medio del 2.4). Ahora `float` y `\floatplacement{figure}{H}` van en `CABECERA`.
  2. Se repuso la **tabla del top 10 del 1.2**: la entrega pide "tablas de resultados" y en la captura chica del 1.5 no se leía.
  3. Se aclaró que los tiempos del Ej. 2 son la mediana del runner y que las capturas muestran una corrida suelta.
  4. En el 3.2 se agregó cómo el split del pipeline reparte las relaciones (test, train y features).
  5. Se agregó un **anexo con los 5 vectores node2vec completos** (el 3.1 pide "el vector de 5 nodos").

## Resultado

- `outputs/informe/TP2_Trabajo2_informe.pdf`: **8 páginas** (el máximo permitido) y todas las imágenes son capturas reales.
- `outputs/entrega/TP2_Trabajo2_Adell_Giannice_Mazzola.zip` (≈1,5 MB): los 4 `.cypher`, `notebook/ej3_4_pairre.ipynb` (7 de 7 celdas ejecutadas) e `informe/TP2_Trabajo2_informe.pdf`. No incluye `.env` ni archivos del skill.
- Falta solamente que el grupo suba el zip al EVA.
