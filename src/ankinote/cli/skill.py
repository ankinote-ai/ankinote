"""``ankinote skill install``: put the bundled agent skill where agents find it.

The skill ships in the wheel (``ankinote/skills/ankinote-cli``) so a ``uvx``
or ``uv tool`` install can hand it to any agent on the machine, not only to
agents working inside a checkout of this repository.
"""

import shutil
from importlib.resources import as_file, files
from pathlib import Path

import click

SKILL_NAME = "ankinote-cli"
DEFAULT_SKILL_DIRS = (Path("~/.claude/skills"), Path("~/.agents/skills"))


def install_skill(skills_dir: Path) -> Path:
    """Copy the bundled skill into ``skills_dir``, replacing an older copy.

    A symlink in the way (e.g. to a checkout) is removed, never followed.

    :returns: the installed skill's folder.
    """
    target = skills_dir / SKILL_NAME
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.exists():
        shutil.rmtree(target)
    skills_dir.mkdir(parents=True, exist_ok=True)
    with as_file(files("ankinote") / "skills" / SKILL_NAME) as source:
        shutil.copytree(source, target)
    return target


@click.group()
def skill() -> None:
    """Install the agent skill that teaches AI agents to use this CLI."""


@skill.command("install")
@click.option(
    "--dir",
    "skills_dirs",
    multiple=True,
    type=click.Path(file_okay=False, path_type=Path),
    help=(
        "Skills folder to install into; repeatable. "
        "[default: ~/.claude/skills and ~/.agents/skills]"
    ),
)
def install(skills_dirs: tuple[Path, ...]) -> None:
    """Copy the ankinote-cli skill into your agents' skills folders.

    Claude Code reads ~/.claude/skills; Codex and other agents that follow
    the Agent Skills convention read ~/.agents/skills. Run it again after
    upgrading ankinote to update the skill.
    """
    targets = skills_dirs or tuple(path.expanduser() for path in DEFAULT_SKILL_DIRS)
    click.echo(f"Installed the {SKILL_NAME} skill to:")
    for skills_dir in targets:
        click.echo(f"  {install_skill(skills_dir)}")
