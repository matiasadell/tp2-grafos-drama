# Expanded Prompt: [Project Name]

> Approved [date] — the source of truth for PLAN.md and CLAUDE.md. This combined file is temporary (deleted in Phase 5); each section below also gets written out as its own persistent file under `prompts/{section_name}.md` — or one file per subsection, `prompts/{section_name}_{topic_slug}.md`, for any section split into subsections — see `references/prompt_sections.md`.

## Role

[The posture Claude Code should build from for this project.]

## Objective

[What's being built and why, in the user's own framing.]

## Context

[Reference material that already exists and matters here — most often theory/class material for a university project, living in `context/`. List the relevant files and why each matters, or state there's none. Split into named subsections, e.g. `### ER diagrams` / `### Normalization theory`, if distinct topics here will map to different PLAN.md tasks.]

## Constraints

[Language, framework, hosting, solo vs. shared build, course/professor requirements — deadline, required tools, submission format — whatever's already decided. Split into named subsections, e.g. `### Tech stack` / `### Deadline` / `### Deployment`, if different tasks will need different slices of this.]

## Non-goals

[What's deliberately not being built as part of this project.]

## Definition of done

[The criteria that confirm this actually works, not just that the files exist.]

<!--
Any section above may be split into subsections instead of one flat block, when it covers more than one topic that different PLAN.md tasks will need separately:

## Constraints

### Tech stack
[...]

### Deadline
[...]

Each subsection becomes its own file at Phase 2 step 3: `prompts/constraints_tech_stack.md`, `prompts/constraints_deadline.md`, etc. Delete this comment before showing the draft for approval.
-->
