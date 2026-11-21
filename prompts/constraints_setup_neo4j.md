# Constraints — Setup de Neo4j y credenciales

1. Claude descarga el dump (hecho).
2. El grupo, en Desktop, crea un DBMS nuevo desde el dump (la consigna dice arrastrarlo a *Files* y elegir «Create new DBMS from dump»; en Desktop 2 es *Create instance* con el archivo) y activa GDS y APOC.
3. Claude ajusta la memoria en el `neo4j.conf` de ese DBMS.

No se usa `LOAD CSV`. La contraseña va en un **`.env` que crea el usuario** en la raíz (`NEO4J_PASSWORD=...`), y ese archivo queda fuera de git y del zip. Claude ejecuta todo (cypher-shell o driver de Python) y guarda cada resultado en `outputs/` como CSV, JSON o texto.
