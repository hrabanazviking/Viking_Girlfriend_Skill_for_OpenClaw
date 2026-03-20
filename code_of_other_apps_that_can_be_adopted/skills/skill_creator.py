# clawlite/skills/skill_creator.py
"""Programmatic skill scaffolding and packaging utilities.

Inspired by nanobot's skills/skill-creator/scripts/init_skill.py and package_skill.py.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path


_SKILL_TEMPLATE = """\
---
name: {name}
description: {description}
always: false
---

# {title}

[TODO: Describe what this skill does and when to use it.]

## Usage

[TODO: Instructions for the agent on how to use this skill.]

## Notes

[TODO: Additional context, constraints, or examples.]
"""

_MAIN_SCRIPT_TEMPLATE = """\
#!/usr/bin/env python3
\"\"\"Main script for the {name} skill.\"\"\"


def main() -> None:
    # TODO: implement skill logic
    pass


if __name__ == "__main__":
    main()
"""


def normalize_skill_name(raw: str) -> str:
    """Convert skill name to lowercase-hyphen format."""
    raw = str(raw or "").strip()
    raw = re.sub(r"[_\s]+", "-", raw)
    raw = re.sub(r"[^a-zA-Z0-9-]", "", raw)
    return raw.lower().strip("-")


def title_case_skill_name(name: str) -> str:
    """Convert hyphen-name to Title Case for display."""
    return " ".join(word.capitalize() for word in name.split("-"))


def init_skill(
    name: str,
    *,
    base_path: "Path | str | None" = None,
    include_scripts: bool = False,
    description: str = "",
) -> Path:
    """Scaffold a new skill directory with SKILL.md.

    Args:
        name: Skill name (will be normalized to hyphen-case).
        base_path: Directory to create the skill in. Defaults to cwd.
        include_scripts: If True, create scripts/ subdir with main.py.
        description: Optional description for frontmatter.

    Returns:
        Path to the created skill directory.

    Raises:
        FileExistsError: If the skill directory already exists.
        ValueError: If name is empty after normalization.
    """
    normalized = normalize_skill_name(name)
    if not normalized:
        raise ValueError(f"Invalid skill name: {name!r}")

    base = Path(base_path or ".").expanduser().resolve()
    skill_dir = base / normalized
    if skill_dir.exists():
        raise FileExistsError(f"Skill directory already exists: {skill_dir}")

    skill_dir.mkdir(parents=True)

    title = title_case_skill_name(normalized)
    desc_line = str(description or "").strip() or "[TODO: one-line description of when this skill triggers]"
    content = _SKILL_TEMPLATE.format(name=normalized, title=title, description=desc_line)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    if include_scripts:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "main.py").write_text(
            _MAIN_SCRIPT_TEMPLATE.format(name=normalized), encoding="utf-8"
        )
        (scripts_dir / "__init__.py").write_text("", encoding="utf-8")

    return skill_dir


def package_skill(skill_path: "Path | str", output_dir: "Path | str | None" = None) -> Path:
    """Package a skill directory into a .skill ZIP archive.

    Args:
        skill_path: Path to the skill directory (must contain SKILL.md).
        output_dir: Where to write the .skill file. Defaults to parent of skill_path.

    Returns:
        Path to the created .skill file.

    Raises:
        FileNotFoundError: If SKILL.md is missing.
        ValueError: If skill_path contains unsafe entries (symlinks, path traversal).
    """
    skill_dir = Path(skill_path).expanduser().resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    out_dir = Path(output_dir or skill_dir.parent).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{skill_dir.name}.skill"

    _EXCLUDE_DIRS = {".git", ".svn", ".hg", "__pycache__", "node_modules", ".mypy_cache"}

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for entry in sorted(skill_dir.rglob("*")):
            if entry.is_symlink():
                raise ValueError(f"Symlinks not allowed in skill packages: {entry}")
            try:
                entry.relative_to(skill_dir)
            except ValueError:
                raise ValueError(f"Path escapes skill root: {entry}")
            if any(part in _EXCLUDE_DIRS for part in entry.parts):
                continue
            if entry.is_file():
                arcname = entry.relative_to(skill_dir)
                zf.write(entry, arcname)

    return archive_path


def _cli_main(args: "list[str] | None" = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(
        prog="python -m clawlite.skills.skill_creator",
        description="ClawLite skill scaffolding tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create a new skill from template")
    init_p.add_argument("name", help="Skill name (will be normalized to hyphen-case)")
    init_p.add_argument("--path", default=".", help="Base directory (default: cwd)")
    init_p.add_argument("--scripts", action="store_true", help="Include scripts/ directory")
    init_p.add_argument("--description", default="", help="Skill description")

    pkg_p = sub.add_parser("package", help="Package skill into .skill archive")
    pkg_p.add_argument("skill_path", help="Path to skill directory")
    pkg_p.add_argument("--output", default=None, help="Output directory")

    ns = parser.parse_args(args)
    if ns.command == "init":
        skill_dir = init_skill(
            ns.name,
            base_path=ns.path,
            include_scripts=ns.scripts,
            description=ns.description,
        )
        print(f"Created skill: {skill_dir}")
    elif ns.command == "package":
        archive = package_skill(ns.skill_path, output_dir=ns.output)
        print(f"Packaged: {archive}")


if __name__ == "__main__":
    _cli_main()
