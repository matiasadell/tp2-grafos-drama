# Clarifying Questions — Phase 1 Question Bank

Default to asking all of these, not a trimmed subset — only drop one if the user's prompt already answered it explicitly. This bank is a floor, not a ceiling: go well beyond it with ad hoc questions specific to the project, and keep going in further batches until nothing is left unclear. Every answer gets logged to `QUESTIONS.md` as it comes in (see `SKILL.md` Phase 1). When in doubt, ask.

## Scope

- What does this project need to do? What's explicitly out of scope?
- Is there an existing codebase this needs to integrate with, or is it greenfield?

## Audience & constraints

- Who uses this — just the user, a team, external users?
- Any hard constraints already decided (language, framework, hosting, budget, deadline, course/professor requirements)?

## Reference material

- Is there existing material this needs to account for — most often theory/class content for a university project? If it's light, ask the user to show it directly; otherwise note that it'll live in `context/` (see `references/prompt_sections.md` → Context).

## Technical

- Expected scale (one user vs. thousands — this changes the architecture)?
- Does it need to persist data? If so, roughly what kind/shape?
- Any integrations with other services/APIs that are non-negotiable?

## Process

- Is this a solo build, or will someone else review/take over the code?
- Should the plan assume Claude Code builds this autonomously, or in tight back-and-forth with the user?