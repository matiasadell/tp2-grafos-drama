# CLAUDE.md Handoff Guide — Phase 4

CLAUDE.md is not a summary of PLAN.md — Claude Code can read that directly. It's the context that's expensive to re-derive: things Claude Code would otherwise have to guess or ask about.

## What belongs in CLAUDE.md

- Where to find PLAN.md (relative path — should just be `PLAN.md` at the project root, but say so explicitly)
- Where to find reference material, if any (`context/`) — theory/class material or other source docs the project needs to account for
- Conventions not obvious from the code itself (naming, file layout, test location, commit style) — always include that generated artifacts (CSVs, images, JSON dumps, model checkpoints, etc.) go in `outputs/`, per the house layout in `SKILL.md`'s Output structure section
- How to verify a step is actually done — this should already be answered per-task by that task's **Definition of done** field in PLAN.md. Only repeat something here if it's a project-wide check (e.g. a test command) that would be tedious to restate in every task.
- Anything explicitly out of scope, so it isn't "helpfully" added back in

## What doesn't belong

- Restating PLAN.md content
- Aspirational process notes nobody will actually follow
