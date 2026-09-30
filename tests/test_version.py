"""Testes da resolução de versão exibida no app.

A versão é derivada da contagem de commits: ``0.{n // 100}.{n % 100}``.
"""

import subprocess
from pathlib import Path

import pytest

from src.version import (
    UNKNOWN_VERSION,
    _is_dirty,
    _version_from_commits,
    _version_from_pyproject,
    get_version,
    write_build_version,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def fake_git(monkeypatch: pytest.MonkeyPatch):
    """Substitui _run_git/_is_dirty para controlar a saída do git."""

    def _install(rev_count: str, dirty: bool = False) -> None:
        monkeypatch.setattr(
            "src.version._run_git",
            lambda *args, **kwargs: rev_count,
        )
        monkeypatch.setattr("src.version._is_dirty", lambda _root: dirty)

    return _install


@pytest.fixture
def failing_git(monkeypatch: pytest.MonkeyPatch):
    """Simula _run_git devolvendo None (git falhou ou ausente)."""

    monkeypatch.setattr("src.version._run_git", lambda *args, **kwargs: None)


def _git_dir(path: Path) -> Path:
    (path / ".git").mkdir()
    return path


class TestVersionFromCommits:
    def test_returns_none_without_git_dir(self, tmp_path: Path) -> None:
        assert _version_from_commits(tmp_path) is None

    def test_single_commit_is_0_0_1(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("1")

        assert _version_from_commits(tmp_path) == "0.0.1"

    def test_ten_commits_is_0_0_10(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("10")

        assert _version_from_commits(tmp_path) == "0.0.10"

    def test_ninety_nine_commits_is_0_0_99(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("99")

        assert _version_from_commits(tmp_path) == "0.0.99"

    def test_hundred_commits_rolls_minor(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("100")

        assert _version_from_commits(tmp_path) == "0.1.0"

    def test_hundred_and_one_commits(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("101")

        assert _version_from_commits(tmp_path) == "0.1.1"

    def test_two_hundred_fifty_commits(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("250")

        assert _version_from_commits(tmp_path) == "0.2.50"

    def test_dirty_tree_appends_suffix(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("10", dirty=True)

        assert _version_from_commits(tmp_path) == "0.0.10-dirty"

    def test_clean_tree_has_no_suffix(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("10", dirty=False)

        assert _version_from_commits(tmp_path) == "0.0.10"

    def test_returns_none_when_git_fails(self, failing_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)

        assert _version_from_commits(tmp_path) is None

    def test_ignores_non_numeric_count(self, fake_git, tmp_path: Path) -> None:
        _git_dir(tmp_path)
        fake_git("muitos")

        assert _version_from_commits(tmp_path) is None


class TestIsDirty:
    def test_true_when_porcelain_outputs_something(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        class _Completed:
            returncode = 0
            stdout = " M src/utils.py\n"

        monkeypatch.setattr(
            "src.version.subprocess.run",
            lambda *args, **kwargs: _Completed(),
        )

        assert _is_dirty(tmp_path) is True

    def test_false_when_porcelain_empty(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        class _Completed:
            returncode = 0
            stdout = ""

        monkeypatch.setattr(
            "src.version.subprocess.run",
            lambda *args, **kwargs: _Completed(),
        )

        assert _is_dirty(tmp_path) is False

    def test_false_when_git_missing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        def _raise(*_args: object, **_kwargs: object) -> None:
            raise FileNotFoundError("git")

        monkeypatch.setattr("src.version.subprocess.run", _raise)

        assert _is_dirty(tmp_path) is False


class TestVersionFromPyproject:
    def test_reads_project_version(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "app-launcher"\nversion = "1.3.2"\n',
            encoding="utf-8",
        )

        assert _version_from_pyproject(tmp_path) == "1.3.2"

    def test_returns_none_without_file(self, tmp_path: Path) -> None:
        assert _version_from_pyproject(tmp_path) is None

    def test_ignores_version_outside_project_table(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[tool.something]\nversion = "9.9.9"\n\n[project]\nname = "x"\n',
            encoding="utf-8",
        )

        assert _version_from_pyproject(tmp_path) is None

    def test_stops_at_next_table(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\n\n[tool.uv]\nversion = "9.9.9"\n',
            encoding="utf-8",
        )

        assert _version_from_pyproject(tmp_path) is None


class TestGetVersion:
    def test_env_override_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_LAUNCHER_VERSION", "9.9.9-test")

        assert get_version(PROJECT_ROOT) == "9.9.9-test"

    def test_blank_env_override_is_ignored(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("APP_LAUNCHER_VERSION", "   ")
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nversion = "2.0.0"\n', encoding="utf-8"
        )

        assert get_version(tmp_path) == "2.0.0"

    def test_falls_back_to_pyproject(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr("src.version._version_from_commits", lambda _r: None)
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nversion = "2.0.0"\n', encoding="utf-8"
        )

        assert get_version(tmp_path) == "2.0.0"

    def test_falls_back_to_dev_when_nothing_resolves(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr("src.version._version_from_commits", lambda _r: None)
        monkeypatch.setattr("src.version._version_from_pyproject", lambda _r: None)

        assert get_version(tmp_path) == UNKNOWN_VERSION

    def test_never_raises_when_resolvers_break(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        def _boom(_root: Path) -> str:
            raise RuntimeError("git explodiu")

        monkeypatch.delenv("APP_LAUNCHER_VERSION", raising=False)
        monkeypatch.setattr("src.version._version_from_commits", _boom)
        monkeypatch.setattr("src.version._version_from_pyproject", _boom)

        assert get_version(tmp_path) == UNKNOWN_VERSION


class TestWriteBuildVersion:
    def test_writes_resolved_version(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nversion = "2.0.0"\n', encoding="utf-8"
        )
        (tmp_path / "src").mkdir()

        written = write_build_version(tmp_path)

        assert written is not None
        assert written.name == "_build_version.py"
        assert 'BUILD_VERSION = "2.0.0"' in written.read_text(encoding="utf-8")

    def test_skips_file_when_unknown(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()

        assert write_build_version(tmp_path) is None
        assert not (tmp_path / "src" / "_build_version.py").exists()

    def test_overwrites_previous_generation(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nversion = "2.0.0"\n', encoding="utf-8"
        )
        (tmp_path / "src").mkdir()
        target = tmp_path / "src" / "_build_version.py"
        target.write_text('BUILD_VERSION = "0.0.0-stale"\n', encoding="utf-8")

        write_build_version(tmp_path)

        assert "0.0.0-stale" not in target.read_text(encoding="utf-8")


class TestRealRepository:
    def test_resolved_version_matches_real_commit_count(self) -> None:
        """A versão do repo precisa bater com o rev-list --count real."""

        expected = subprocess.run(
            ("git", "rev-list", "--count", "HEAD"),
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if expected.returncode != 0:
            pytest.skip("repositório sem git disponível")

        resolved = _version_from_commits(PROJECT_ROOT)

        assert resolved is not None
        count = int(expected.stdout.strip())
        base = f"0.{count // 100}.{count % 100}"
        assert resolved == base or resolved == f"{base}-dirty"
