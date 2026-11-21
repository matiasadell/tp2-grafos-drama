# Prompt Expansion Guide — Phase 2

The expanded prompt is what Phase 3 (PLAN.md) and Phase 4 (CLAUDE.md) are actually written from — not the user's original one-liner, and not whatever's been said across the conversation. It's drafted as six named sections, each optionally broken into named subsections (see `references/prompt_sections.md`), and needs to stand alone: someone reading only the approved draft should be able to reconstruct the same plan you're about to write.

## What it should cover

- **The original ask**, restated plainly — don't lose the user's own framing or priorities. This is the backbone of the **Objective** section.
- **Everything resolved in Phase 1**: scope and what "done" means, audience, constraints already decided, solo vs. shared build, any reference material to account for (→ **Context**).
- **Explicit non-goals** — what's deliberately out of scope, so later phases don't quietly scope-creep back in.
- **Anything the user said that contradicts a sensible default** — call it out rather than letting it blend in, so it survives into PLAN.md.

## What it shouldn't do

- Invent requirements the user didn't state and didn't confirm in Phase 1. If drafting surfaces something still genuinely unknown, stop and go ask — Phase 1 is a hard gate, so the expanded prompt should never carry forward an unresolved question or a silent assumption.
- Pre-decide architecture or step breakdown — that's PLAN.md's job, one phase later, written by re-reading this file once it's approved.
- Run longer than it needs to. Structured and detailed doesn't mean padded; every sentence should be something Phase 3 or 4 will actually use.

## Where it ends up

Once approved, the same content gets written twice, for different reasons:

- The full draft → `PROMPT.md` at the project root. Temporary — deleted in Phase 5 once PLAN.md and CLAUDE.md exist.
- Each section → its own `prompts/{section_name}.md`, or its own `prompts/{section_name}_{topic_slug}.md` per subsection if it was split (see `references/prompt_sections.md`). Permanent — these are what PLAN.md's steps will later point to for task-specific context, including once Claude Code is implementing.

Draft and show the sections together as one document for approval; only split and write the separate files after the user says yes.

## Approval loop

Show the draft, wait for an explicit approval or a requested change. If the user edits or pushes back, fold that in and show it again — don't treat a non-answer as approval. Only write `PROMPT.md` and the `prompts/` files once the user has actually said yes.