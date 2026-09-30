"""Resolução da versão exibida no app.

A versão é derivada da contagem de commits no repositório: com ``n`` commits o
resultado é ``0.{n // 100}.{n % 100}``, ou seja, 1 commit = ``0.0.1``,
10 commits = ``0.0.10``, 100 commits = ``0.1.0``, 250 = ``0.2.50``. Um working
tree com mudanças não commitadas ganha o sufixo ``-dirty``.

Ordem de precedência:

1. variável de ambiente ``APP_LAUNCHER_VERSION`` (override manual);
2. ``src/_build_version.py``, gerado no build e congelado no bundle, para que o
   binário onefile não dependa de git nem do repositório em tempo de execução;
3. contagem de commits via ``git rev-list --count HEAD``;
4. ``version`` de ``pyproject.toml``;
5. ``"dev"``.
"""

import logging
import os
import subprocess
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)

ENV_OVERRIDE = "APP_LAUNCHER_VERSION"
BUILT_VERSION_MODULE = "_build_version"
UNKNOWN_VERSION = "dev"

_COMMITS_PER_MINOR = 100


def _run_git(*args: str, cwd: Path) -> str | None:
    try:
        completed = subprocess.run(
            ("git", *args),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if completed.returncode != 0:
        return None

    output = completed.stdout.strip()
    return output or None


def _is_dirty(repo_root: Path) -> bool:
    """True quando existe alguma mudança não commitada no working tree."""
    try:
        completed = subprocess.run(
            ("git", "status", "--porcelain"),
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False

    return completed.returncode == 0 and bool(completed.stdout.strip())


def _version_from_commits(repo_root: Path) -> str | None:
    """Deriva a versão da contagem de commits do repositório."""
    if not (repo_root / ".git").exists():
        return None

    count = _run_git("rev-list", "--count", "HEAD", cwd=repo_root)
    if count is None:
        return None

    try:
        total = int(count)
    except ValueError:
        logger.debug(f"rev-list --count devolveu algo inesperado: {count!r}")
        return None

    version = f"0.{total // _COMMITS_PER_MINOR}.{total % _COMMITS_PER_MINOR}"
    if _is_dirty(repo_root):
        version += "-dirty"

    return version


def _version_from_pyproject(repo_root: Path) -> str | None:
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.is_file():
        return None

    try:
        content = pyproject.read_text(encoding="utf-8")
    except OSError:
        return None

    in_project_table = False
    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("["):
            in_project_table = stripped == "[project]"
            continue

        if in_project_table and stripped.startswith("version"):
            _, _, value = stripped.partition("=")
            return value.strip().strip("\"'") or None

    return None


def _version_from_build_module() -> str | None:
    """Lê a versão congelada no bundle, se o build a tiver gravado.

    ``src/_build_version.py`` só existe depois de um build, então o import
    precisa aguentar o módulo ausente sem quebrar o app em modo dev.

    O import é estático de propósito: o PyInstaller só inclui no bundle o que
    ele enxerga por análise estática, então ``importlib`` não serviria aqui.
    """
    try:
        from src._build_version import BUILD_VERSION
    except ImportError:
        return None

    return BUILD_VERSION or None


def get_version(repo_root: Path | None = None) -> str:
    """Devolve a versão para exibição, nunca levanta exceção."""
    override = os.environ.get(ENV_OVERRIDE, "").strip()
    if override:
        return override

    baked = _version_from_build_module()
    if baked:
        return baked

    root = repo_root or Path(__file__).resolve().parent.parent

    for resolver in (_version_from_commits, _version_from_pyproject):
        try:
            resolved = resolver(root)
        except Exception:
            logger.debug(f"falha em {resolver.__name__}", exc_info=True)
            continue

        if resolved:
            return resolved

    return UNKNOWN_VERSION


def write_build_version(repo_root: Path | None = None) -> Path | None:
    """Grava ``src/_build_version.py`` com a versão atual.

    Chamado pelo build antes do PyInstaller para que o binário congelado carregue
    a versão sem precisar de git em tempo de execução. Devolve o caminho
    gerado, ou None quando o versionamento não pôde ser resolvido.
    """
    root = repo_root or Path(__file__).resolve().parent.parent
    resolved = get_version(root)

    if resolved == UNKNOWN_VERSION:
        logger.warning("versão não determinada, _build_version.py não será gerado")
        return None

    target = root / "src" / f"{BUILT_VERSION_MODULE}.py"
    target.write_text(
        f'"""Gerado no build. Não editar."""\n\nBUILD_VERSION = "{resolved}"\n',
        encoding="utf-8",
    )
    logger.info(f"versão para o bundle: {resolved}")

    return target


__all__ = ["get_version", "write_build_version"]
