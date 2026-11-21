# Estado — Verificación de idempotencia (Task 11)

Fecha: 2026-11-21. DBMS `tp2-recommendations` (Neo4j 2026.09.0, GDS 2026.09.0).

## Procedimiento

Se corrieron los 4 scripts en orden (00 → 01 → 02 → 03) **dos veces seguidas** con `python -m src.tp2.run_cypher`, sin tocar la base entre una corrida y otra. Después se compararon todos los CSV de `outputs/resultados/` de la corrida A contra los de la B:

- se ignoran las columnas `*Millis`, que son tiempos de cómputo;
- los números se comparan con una tolerancia relativa de 1e-9;
- los vectores y diccionarios JSON se comparan componente a componente.

## Resultado final

| Corrida | 00_parte_comun | 01_ejercicio1 | 02_ejercicio2 | 03_ejercicio3 |
|---|---|---|---|---|
| A | exit 0 (7 pasos) | exit 0 (12 pasos) | exit 0 (16 pasos) | exit 0 (20 pasos) |
| B | exit 0 (7 pasos) | exit 0 (12 pasos) | exit 0 (16 pasos) | exit 0 (20 pasos) |

CSV comparados: 55 | idénticos (salvo *Millis y tolerancia relativa 1e-9): 55
| Archivo | Diferencias | Máx. dif. relativa |
|---|---|---|
| (ninguno) | — | — |

**Conclusión:** los scripts son reejecutables y todos los entregables numéricos son reproducibles, incluidos los embeddings node2vec, el AUCPR del pipeline (0,8316), el top 5 de predicciones y el KNN. Los tiempos de PROFILE del Ej. 2 varían entre corridas, como es esperable; el informe usa la mediana de 20.

## Hallazgo durante la verificación (corregido)

En la primera doble corrida, la **betweenness con muestreo** variaba hasta un 0,7 % entre corridas, y con eso cambiaba el orden del top 10, aunque se usaba `samplingSeed: 42`. Dentro de una misma proyección, el 1.2 y el 1.5a coincidían.

- Agregar `readConcurrency: 1` a la proyección `califW` **no alcanzó**: las diferencias seguían, de hasta un 2 %.
- La causa es la ejecución paralela de la betweenness: con varios hilos, la selección de nodos fuente del muestreo no es reproducible.
- **Corrección:** `concurrency: 1` en las 4 llamadas de betweenness (1.2 y 1.5 stream/stats/write). Se mantuvo `readConcurrency: 1` en las proyecciones `califW` de los Ej. 1 y 3.
- Con eso, 55 de 55 CSV quedan idénticos. El top 10 final cambió apenas respecto de la primera versión: *Crystal Spencer* entra décima en lugar de *Anthony Cook*.

El notebook PairRE también se ejecutó dos veces (antes y después de limpiar la salida de tqdm), con métricas y hechos idénticos: MRR 0,10458, Hits@10 0,19209, *Vanilla Sky*, *The African Queen* y *Devil in a Blue Dress*.
