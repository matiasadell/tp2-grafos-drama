# PLAN.md Step Structure

## Layout

`#` headings mark phases of the plan. `##` headings mark individual tasks/steps, numbered sequentially through the *whole* plan (not reset per phase), so any task can be referenced unambiguously elsewhere (CLAUDE.md, prompts/, conversation, etc.):

```
# Phase 1 — <phase name>

## Task 1 — <short task title>
**Prompts:** prompt1.md, prompt2.md
**Context:** context/file1.pdf
**Objective:** <one-line summary of what this task accomplishes>
**Description:** <fuller context — approach, edge cases, anything
non-obvious Claude Code needs to do this specific task well>
**Outputs:** <every filesystem change this task makes — see
"Materialization" below>
**Definition of done:** <how to confirm this task actually worked — see
"Definition of done" below>

## Task 2 — <short task title>
...

# Phase 2 — <phase name>

## Task 3 — <short task title>
...
```

## Fields

- **Prompts** — the `prompts/{section}.md` files relevant to *this* task specifically, not the whole expanded prompt. This is how a task gives Claude Code narrow, fresh context instead of re-reading everything every time.
- **Context** — the `context/` files (if any) this task needs — reference material the user placed manually, most often theory/class documents for a university project. Separate from **Prompts**: `prompts/` is the expanded-prompt sections the skill wrote, `context/` is source material the user supplied. Write `none` when a task doesn't need any.
- **Objective** — one line. What this task is for.
- **Description** — the detail Objective doesn't have room for.
- **Outputs** — never empty. See "Materialization" below.
- **Definition of done** — never empty. See "Definition of done" below.

## Materialization — every task must leave a filesystem trace

Hard rule, not a suggestion: every task, no exceptions, must result in at least one concrete filesystem change, listed under **Outputs**. A "change" is one of: a file or folder created, modified, appended to, or deleted — whether Claude Code does that directly, or a script/command it runs does it on its behalf.

Why: tasks can get interrupted — token limits, API errors, context overflow, a session restarting. If progress only exists as conversation state, an interruption loses it. If progress exists as files on disk, the next session can look at the filesystem and know exactly which tasks actually finished, instead of trusting a memory of "what I think I did." File operations are the checkpoint.

This applies even to tasks that are pure analysis, research, or verification, with no natural file to produce. Those don't get a pass — they still write a file recording what was checked and what was found (a short status/findings note is enough). A task with nothing under Outputs is, as far as the next session is concerned, a task that didn't happen.

List each output as `path` — `operation`, e.g.:

```
**Outputs:**
- `src/auth/login.py` — created
- `src/auth/__init__.py` — modified (added import)
- `progress/task_3_findings.md` — created (this task was analysis-only;
  the finding itself is the materialization)
```

## Definition of done — the check on top of Outputs

Outputs says what got produced. **Definition of done** says how to confirm it's actually correct, not just present. The two are checked differently:

- A check on the Outputs themselves (open `login.py`, confirm it exports a working `login()` function).
- A behavioral/functional check that doesn't have to touch any particular file at all (run `pytest`, confirm all tests pass; start the server, hit `/health`, confirm `200`; execute the script, confirm it produces the expected result).

Unlike Outputs, Definition of done is exempt from the materialization rule above: its result doesn't need a new file of its own. Once Claude Code runs the check, a short summary back to the user — pass/fail and why — is enough. The durable checkpoint for the task is already covered by Outputs; Definition of done is just confirmation on top of it, so there's no need to also persist the confirmation itself.

```
**Definition of done:** Run `pytest tests/test_login.py` — all tests
pass. Manually confirm `login()` rejects an empty password.
```