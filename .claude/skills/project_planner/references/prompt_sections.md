# Expanded Prompt Sections

The expanded prompt is split into six named sections. Once the draft is approved (Phase 2), each one becomes its own persistent file under `prompts/{section_name}.md`, so PLAN.md's tasks can later point a given task at just the section(s) it actually needs instead of the whole expanded prompt (see **Prompts** in `references/plan_structure.md`).

## Splitting a section into subsections

The six sections below are a floor, not a ceiling on granularity. Any section that actually covers more than one distinct topic should be broken into named subsections at draft time, each becoming its own file: `prompts/{section_name}_{topic_slug}.md` instead of one `prompts/{section_name}.md`. For example, a project with a hard deadline, a mandated tech stack, and a specific deployment target might split Constraints into `prompts/constraints_deadline.md`, `prompts/constraints_tech_stack.md`, and `prompts/constraints_deployment.md`.

The test for whether to split: would different PLAN.md tasks plausibly want different slices of this section in their **Prompts** field? If yes, split along those lines — the goal is that a task can list exactly the narrow context it needs (possibly several small files) instead of being pointed at one broad file that drags in topics irrelevant to that task. If a section is already one coherent topic (a short Role, a single-sentence Objective), leave it as one file — splitting it further would just be noise.

This is a per-project judgment call made while drafting, informed by looking ahead at the kind of tasks PLAN.md will likely need — not a fixed template applied the same way every time.

## Role

`prompts/role.md` — the posture Claude Code should build from: not "a helpful assistant" but something like "a backend engineer building a REST API for a university database-systems course." Sets the frame for the judgment calls Claude Code makes without being asked.

## Objective

`prompts/objective.md` — what's being built and why, restated plainly from the user's own framing and priorities (Phase 1), not invented.

## Context

`prompts/context.md` — reference material that already exists and matters for this build. Most commonly: theory or class material for a university project. These files live in `context/`, placed manually by the user — if they're light enough, the user shows them directly during Phase 1/2 so the plan itself can account for them; otherwise they get dropped into `context/` without necessarily being shown in full. This section lists which `context/` files are relevant and why, e.g. "see `context/clase_5_normalizacion.pdf` for the normal-form definitions this project must follow." If there's no reference material, say so explicitly rather than leaving the section empty.

## Constraints

`prompts/constraints.md` — language/framework, hosting, solo vs. shared build, and anything the course/professor mandates: a submission deadline, a required library or tool taught in class, a specific submission format (notebook, repo, written report). Anything already decided that later phases shouldn't second-guess.

## Non-goals

`prompts/non_goals.md` — what's deliberately not being built as part of this project, stated as a plain list. Distinct from **Definition of done**: this is "what we're not doing," not "how we know we're done." Exists so Claude Code doesn't "helpfully" add it back later.

## Definition of done

`prompts/definition_of_done.md` — the criteria that confirm the project actually works, not just that files exist. This is the project-level version; Phase 3 also gives each individual task its own **Definition of done** field.