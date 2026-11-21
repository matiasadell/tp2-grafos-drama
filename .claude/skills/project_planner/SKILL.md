---
name: project_planner
description: >-
  Turns a rough project idea or prompt into a complete, structured plan
  that Claude Code can implement directly — an expanded, user-approved
  prompt, a step-by-step PLAN.md, and a CLAUDE.md handoff file. Use this
  skill whenever the user describes something they want to build (an
  app, script, feature, internal tool, or side project) and wants it
  planned, spec'd, scoped, or broken into steps before coding starts.
  Trigger on phrases like "plan this project", "spec this out", "design
  the architecture for X", "break this into steps for Claude Code", or "I
  want to build X, help me plan it" — and trigger proactively when the
  user describes a non-trivial build from scratch even without using the
  word "plan", since jumping straight to code on an unplanned project is
  usually a mistake. Do not use for small, well-defined one-off scripts,
  or for planning unrelated to software, like event planning or travel
  planning.
---

# Project Planner

## Purpose

Take a prompt describing something the user wants built, and turn it into a project plan thorough enough that Claude Code (or another implementing agent) can start writing code without having to re-derive scope, architecture, or sequencing decisions on its own.

The output isn't prose for a human to read once — it's a small set of documents meant to live inside the project's repo and be read by Claude Code as working context.

## Paths

This skill's own files live at `<project_root>/.claude/skills/project_planner/` — everywhere below that a path starts with `references/`, `assets/`, or `scripts/`, it means relative to *this skill's own directory*, not the project. Everything else this workflow reads or writes — `QUESTIONS.md`, `PROMPT.md`, `PLAN.md`, `CLAUDE.md`, `prompts/`, `context/`, `src/`, `docs/` — lives at the project root, i.e. the directory Claude Code is already running in. These are two different directories; don't resolve a bare `references/...` path against the project root, or a bare `PLAN.md` against the skill's own directory.

## Before you start

Read `references/planning_methodology.md`. That file holds planning practices refined by hand over real projects — treat it as more authoritative than the general guidance below whenever the two disagree. If it's still thin/empty, fall back to the workflow described here.

## Workflow

### Phase 1 — Clarify

Don't plan against an ambiguous prompt. This phase ends only when there is zero unresolved doubt — not when the batch feels "big enough."

0. Before asking anything, run `scripts/scaffold_project.py` to materialize the project root's folder structure (`src/`, `docs/`, `prompts/`, `context/`, `outputs/`) and drop in blank `PLAN.md`/`CLAUDE.md` templates. This always runs — the plan is never the deliverable on its own; it exists to be implemented, so the project layout it'll be implemented into should exist from the start. Skip it and lay the structure down by hand only if running the script is impractical for the situation.
1. Ask questions in batched rounds, not one at a time. Start from `references/clarifying_questions.md`; only skip a question there if the user's prompt already answered it explicitly and unambiguously (not "probably implied" — actually stated).
2. Go heavily beyond the bank. The file is a floor, not a ceiling — for any real unknown this specific project raises, ask an ad hoc question about it even if nothing in the bank prompted it. Do not hold back ad hoc questions to keep the batch short; more questions is the correct outcome, not a failure mode.
3. After each round of answers, write every Q/A pair to `QUESTIONS.md` at the project root (the directory Claude Code is already running in), appending as you go, in the form:

   ```
   Q: <question as asked>
   A: <user's answer, verbatim or lightly cleaned up>
   ```

4. Keep asking further rounds — informed by the answers so far, since one answer often exposes the next unknown — until you genuinely have no more questions left to ask. Do not stop early or decide something is "probably fine to assume." There is no "flag it and continue" path: everything downstream has to trace back to an answer actually logged in `QUESTIONS.md`.
5. After the plan is approved, if a question you asked (bank or ad hoc) looks like it'll recur for other projects, flag it to the user rather than writing it anywhere yourself — this skill's files are copied into each project from a canonical source folder (see `references/planning_methodology.md`), so a session running from a copy can't grow the bank by editing its own local `references/clarifying_questions.md`; that copy is never read again once this project is done. The user folds worthwhile ones into the canonical file themselves, e.g. while reviewing the Phase 2 approval checkpoint.

### Phase 2 — Expand the prompt, then get it approved

The user's original prompt is usually short. Don't plan straight off of it alone, and don't plan from conversation memory either — re-read both the original short prompt and the full `QUESTIONS.md` written in Phase 1, and turn them into a long, structured prompt, then get it approved before generating anything.

This expansion is not a summary or synthesis — it must not omit or compress any detail from the short prompt or from any Q/A pair in `QUESTIONS.md`. The job is to take everything that was said across both sources and restructure it into a well-written, specifically organized prompt — better redacted and better sequenced than the raw inputs, but strictly a superset of their content, never a trimmed-down version. Every detail from the short prompt and every answer in `QUESTIONS.md` must appear somewhere in the expanded prompt; if a section doesn't trace back to the short prompt or a Q/A pair, that's a sign Phase 1 wasn't actually finished.

1. Draft the expanded prompt as six named sections — Role, Objective, Context, Constraints, Non-goals, Definition of done (see `references/prompt_sections.md` for what belongs in each). Within any section that covers more than one distinct topic, break it into named subsections — e.g. Constraints might split into "Tech stack," "Deadline," "Deployment" — whenever different PLAN.md tasks will plausibly need different slices of it. Don't split a section that's already one coherent topic just for the sake of splitting. See `references/prompt_expansion.md` for what the content should cover, and `assets/templates/PROMPT_template.md` for the shape.
2. Show the full draft to the user and ask them to approve it or edit it. Don't move on without an explicit yes — this is the one checkpoint where a wrong assumption gets caught before any project files exist.
3. Once approved, write two things at the project root:
   - The full approved prompt → `PROMPT.md`. Temporary, deleted in Phase 5.
   - Each section, or each subsection if the section was split → its own file under `prompts/`: `prompts/{section_name}.md` for an unsplit section, or `prompts/{section_name}_{topic_slug}.md` per subsection (e.g. "Definition of done" → `prompts/definition_of_done.md`; a split "Constraints" → `prompts/constraints_tech_stack.md`, `prompts/constraints_deadline.md`, etc.). This folder is **not** temporary — it's part of the final project, since PLAN.md's steps will later point into it for task-specific context (see Phase 3), and a task can list more than one of these files at once.

From here on, treat `PROMPT.md` — not the original one-line prompt, and not your memory of the conversation — as the source of truth. Re-read the file rather than relying on context; it's the one thing that's actually been confirmed correct.

### Phase 3 — Write PLAN.md

Read `PROMPT.md` and fill in `PLAN.md` based on it, following the shape of `assets/templates/PLAN_template.md`. `PLAN.md` already exists as that unfilled template from Phase 1's scaffold step — replace its placeholder content with the real plan rather than treating this as creating a new file. This is the single planning document: it replaces what used to be a separate brief, architecture doc, and task list — the problem/goal, the key technical decisions, and the step-by-step breakdown of how the project gets built all live here now.

Each step's structure is defined in `references/plan_structure.md`: `#` headings mark phases, `##` headings mark sequentially numbered tasks, and every task has six fields — **Prompts** (which `prompts/{section}.md` files are relevant to *this* task), **Context** (which `context/` files, if any, this task needs), **Objective**, **Description**, **Outputs**, and **Definition of done**.

**Outputs is the load-bearing field.** Every task must leave at least one concrete filesystem trace — a file or folder created, modified, appended to, or deleted, whether directly or via code execution — listed under Outputs. This applies even to analysis-only tasks: if there's no natural file to produce, write a short status/findings note and list that instead. A task with nothing under Outputs didn't materialize, and won't survive an interrupted session (token limits, API errors, context overflow) — the filesystem state is the checkpoint, not the conversation.

**Definition of done is the check on top of that.** It's how to confirm the task actually worked — a check on the Outputs themselves, or a behavioral check that doesn't have to touch any particular file (run the tests, hit the endpoint, execute the script). Unlike Outputs, its result doesn't need a new file of its own — once Claude Code verifies it, a short pass/fail summary back to the user is enough; the durable checkpoint is already covered by Outputs. See `references/plan_structure.md` for the exact format.

### Phase 4 — Hand off to Claude Code

Fill in `CLAUDE.md` at the project root, following the shape of `assets/templates/CLAUDE_md_template.md`. As with `PLAN.md` in Phase 3, it already exists as the unfilled template from Phase 1's scaffold step — replace its placeholder content rather than treating this as creating a new file. See `references/claude_code_handoff.md` for what makes a CLAUDE.md actually useful versus just restating PLAN.md.

### Phase 5 — Clean up

Once `PLAN.md`, `CLAUDE.md`, and any scaffolded folders exist, delete `QUESTIONS.md` and `PROMPT.md` only. Both were scaffolding to get a good plan written and approved, not part of the deliverable — leaving them behind would just be stale copies of what's now properly captured in `PLAN.md` and `prompts/`.

Do **not** delete `prompts/`. Unlike `PROMPT.md`, that folder is part of the final project — PLAN.md's steps reference it for task-specific context, including later, while Claude Code is actually implementing.

## Output structure

A finished plan produces this layout at the project root:

```
<project-name>/
├── CLAUDE.md       # handoff context Claude Code reads every session
├── PLAN.md         # step-by-step plan for how the project gets built
├── prompts/        # one file per expanded-prompt section, or per
│                   # subsection if a section was split (see
│                   # references/prompt_sections.md)
│   ├── role.md
│   ├── objective.md
│   ├── context.md
│   ├── constraints.md
│   ├── non_goals.md
│   └── definition_of_done.md
├── context/        # reference material the user placed manually
│                   # (e.g. theory/class files) — optional, project-specific
├── src/            # all code
├── docs/           # documentation/reports (not docstrings)
└── outputs/        # generated artifacts from running code — CSVs,
                     # images, JSON dumps, model checkpoints, etc.
```

`QUESTIONS.md` and `PROMPT.md` exist at this same location while Phases 1-4 run, but both get deleted in Phase 5 — they're scaffolding, not part of the final output. `prompts/`, unlike them, is permanent: PLAN.md's steps reference individual files in it for task-specific context. `context/`, when used, is also permanent and user-managed — this skill doesn't create or populate it, but PLAN.md tasks may point into it via the **Context** field. `scripts/scaffold_project.py` creates `prompts/`, `context/`, `src/`, `docs/`, and `outputs/` as empty folders at the start of Phase 1, along with the blank `PLAN.md`/`CLAUDE.md` templates Phases 3–4 fill in; `context/` may stay empty if the project has no reference material to place there.

**Convention: code-run outputs go in `outputs/`, nowhere else.** Anything a script or program produces as a side effect of running — a CSV, an image, a JSON dump, a trained model checkpoint — belongs in `outputs/`, not scattered next to the source that generated it, not in `docs/`. `src/` is for code; `docs/` is for documentation/reports written *about* the project; `outputs/` is for whatever the code actually produces when run. PLAN.md tasks whose **Outputs** field includes generated artifacts (as opposed to source files) should point at a path under `outputs/`, and CLAUDE.md's Conventions section should restate this so Claude Code follows it while implementing.

## See also

- `references/planning_methodology.md` — hand-edited practices, read first
- `references/clarifying_questions.md` — question bank for Phase 1
- `references/prompt_expansion.md` — Phase 2, what the expanded prompt should cover
- `references/prompt_sections.md` — Phase 2, the six sections and their prompts/ filenames
- `assets/templates/PROMPT_template.md` — Phase 2, shape of the expanded prompt
- `references/plan_structure.md` — Phase 3, the phase/task/Outputs format every step follows
- `references/claude_code_handoff.md` — what belongs in CLAUDE.md
- `scripts/scaffold_project.py` — Phase 1, materializes the project's folder structure and blank PLAN.md/CLAUDE.md templates up front
