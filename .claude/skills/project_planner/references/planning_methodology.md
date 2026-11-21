# Planning Methodology — Hand-Edited Notes

This file is the source of truth for the practices that have actually worked across real projects. It starts thin on purpose — fill it in as you notice patterns, rather than trying to write the "complete" version upfront.

When `project_planner` runs, it reads this file before anything else. If something here conflicts with the generic guidance in `SKILL.md`, this file wins.

## What to capture here

- Planning habits that consistently produced a plan Claude Code could run with, without back-and-forth (e.g. "always pin exact dependency versions in PLAN.md" or "steps under ~30 min of work get merged together")
- Mistakes seen in past plans, and the rule that would have prevented them
- Preferences for how you like plans structured (ordering, tone, level of detail) that differ from the SKILL.md defaults
- Tech-stack defaults you reach for unless the project calls for something else, so the model doesn't re-litigate the same choice every time

## Notes

- This skill's canonical source is `C:\Users\facum\Documents\Coding\claude skills\project_planner` — the folder `claude_serverless/backend/skills.py` copies from (`config.SKILLS_DIR`) into every session that selects this skill, at `<project>/.claude/skills/project_planner/`. A session running from a copy edits a throwaway instance of these files, not this one. When Phase 1 step 5 flags a recurring question, add it to *this* file's `references/clarifying_questions.md` by hand — not the copy inside whatever project you're planning.
