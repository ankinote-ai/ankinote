"""``ankinote skill install`` — copy the bundled agent skill into skill folders."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from ankinote.cli.main import cli

REPO = Path(__file__).resolve().parents[2]
BUNDLED = REPO / "src" / "ankinote" / "skills" / "ankinote-cli"


def _install(*args: str) -> str:
    result = CliRunner().invoke(cli, ["skill", "install", *args])
    assert result.exit_code == 0, result.output
    return result.output


def _tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_bundled_skill_is_the_repo_skill():
    """The repo's .agents copy is a link to the bundled one, not a fork."""
    assert (
        (BUNDLED / "SKILL.md")
        .read_text(encoding="utf-8")
        .startswith("---\nname: ankinote-cli\n")
    )
    assert (REPO / ".agents" / "skills" / "ankinote-cli").resolve() == BUNDLED


def test_install_copies_the_whole_skill_into_each_dir(tmp_path: Path):
    first, second = tmp_path / "a", tmp_path / "b"

    output = _install("--dir", str(first), "--dir", str(second))

    for skills_dir in (first, second):
        assert _tree(skills_dir / "ankinote-cli") == _tree(BUNDLED)
        assert str(skills_dir / "ankinote-cli") in output
    assert "references/stem.md" in _tree(first / "ankinote-cli")


def test_install_defaults_to_claude_and_agents_skill_dirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("HOME", str(tmp_path))

    _install()

    for skills_dir in (".claude/skills", ".agents/skills"):
        installed = tmp_path / skills_dir / "ankinote-cli"
        assert _tree(installed) == _tree(BUNDLED)


def test_reinstall_replaces_an_older_copy(tmp_path: Path):
    old = tmp_path / "ankinote-cli"
    (old / "references").mkdir(parents=True)
    (old / "SKILL.md").write_text("old", encoding="utf-8")
    (old / "references" / "gone.md").write_text("old", encoding="utf-8")

    _install("--dir", str(tmp_path))

    assert _tree(old) == _tree(BUNDLED)


def test_reinstall_replaces_a_symlink_without_touching_its_target(tmp_path: Path):
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    (checkout / "SKILL.md").write_text("dev copy", encoding="utf-8")
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "ankinote-cli").symlink_to(checkout)

    _install("--dir", str(skills_dir))

    installed = skills_dir / "ankinote-cli"
    assert not installed.is_symlink()
    assert _tree(installed) == _tree(BUNDLED)
    assert _tree(checkout) == {"SKILL.md": "dev copy"}
