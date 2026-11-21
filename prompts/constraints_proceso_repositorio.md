# Constraints — Proceso y repositorio

- Claude trabaja **de forma autónoma** y solo se detiene en los pasos manuales: crear el DBMS, el `.env` y las capturas.
- **git local, sin remoto**, con `.gitignore` (`.env`, outputs pesados, checkpoints) y un commit por tarea.
- Los archivos del skill (`SKILL.md`, `references/`, `assets/`, `scripts/`, `evals/`) se mueven a `.claude/skills/project_planner/`.
- Todo va en español (comentarios, nombres libres, informe). Los nombres de algoritmos se mantienen; por ejemplo, la propiedad se llama `betweenness`.
