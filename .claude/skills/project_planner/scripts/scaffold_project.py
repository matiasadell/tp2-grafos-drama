#!/usr/bin/env python3
"""
Scaffold project_planner's output documents into a project directory.

Copies the template files into the project directory as-is. Always
creates the default `src/`, `docs/`, `prompts/`, `context/`, and
`outputs/` folders (the house layout), plus any additional folders
passed in. Runs against the current directory by default — the project
directory Claude Code is already running in — not a new directory the
script has to create.

`outputs/` is where generated artifacts from running code belong — CSVs,
images, JSON dumps, model checkpoints, anything a script produces as a
side effect of running, as opposed to source code (`src/`) or
documentation (`docs/`). This script only creates the empty folder; see
SKILL.md's Output structure section for the convention itself.

Usage (run from the project root, since target_dir defaults to "."
— the current directory — and this script lives under
<project_root>/.claude/skills/project_planner/scripts/):
    python .claude/skills/project_planner/scripts/scaffold_project.py \\
        [target_dir] [--folders tests] [--templates-dir path]

Typical use: run this at the very start of Phase 1 in SKILL.md, before
any clarifying questions are asked, so the project's folder structure
and blank PLAN.md/CLAUDE.md templates exist from the outset. Phases 2-4
then fill in the real content over what this script laid down: Phase 2
writes PROMPT.md and the individual prompts/{section}.md files into the
empty prompts/ folder this script already created (PROMPT.md gets
deleted afterward in Phase 5, prompts/ persists — so neither PROMPT.md
nor the section files are templates copied by this script), and Phases
3-4 overwrite the placeholder PLAN.md/CLAUDE.md content with the real
plan and handoff notes. Skip this script entirely and write the files
directly with Write/Edit if that's simpler for the situation.
"""
import argparse
from pathlib import Path

TEMPLATE_FILES = {
    "PLAN_template.md": "PLAN.md",
    "CLAUDE_md_template.md": "CLAUDE.md",
}

DEFAULT_FOLDERS = ["src", "docs", "prompts", "context", "outputs"]


def scaffold(target_dir: Path, templates_dir: Path, folders):
    target_dir.mkdir(parents=True, exist_ok=True)

    for template_name, output_name in TEMPLATE_FILES.items():
        src = templates_dir / template_name
        if not src.exists():
            print(f"skip (not found): {src}")
            continue
        content = src.read_text()
        dest = target_dir / output_name
        dest.write_text(content)
        print(f"wrote {dest}")

    all_folders = list(dict.fromkeys(DEFAULT_FOLDERS + list(folders or [])))
    for folder in all_folders:
        (target_dir / folder).mkdir(parents=True, exist_ok=True)
        print(f"created folder {target_dir / folder}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Project directory to scaffold into (defaults to the current directory)",
    )
    parser.add_argument(
        "--templates-dir",
        default=str(Path(__file__).resolve().parent.parent / "assets" / "templates"),
        help="Directory containing the *_template.md files",
    )
    parser.add_argument(
        "--folders",
        nargs="*",
        default=[],
        help="Extra folders beyond the defaults (src, docs, prompts, context, outputs) — e.g. tests",
    )
    args = parser.parse_args()

    scaffold(
        Path(args.target_dir),
        Path(args.templates_dir),
        args.folders,
    )


if __name__ == "__main__":
    main()
