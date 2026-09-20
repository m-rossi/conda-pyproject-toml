import sys
from pathlib import Path

import pytest

from .. import PyProjectTomlSpec

PYPROJECT_CONTENT = """
[project]
name = "example-project"
requires-python = ">=3.10"
dependencies = [
  "numpy>=1.26",
  "requests==2.31.0",
  "tomli>=2.4.1; python_version < '3.11'",
  "pywin32>=312; sys_platform == 'win32'",
  "some-osx-package>=1.0; sys_platform == 'darwin'",
]

[project.optional-dependencies]
test = [
  "pytest",
]
"""


@pytest.fixture
def pyproject_file(tmp_path: Path) -> Path:
    path = tmp_path / 'pyproject.toml'
    path.write_text(PYPROJECT_CONTENT)
    return path


def test_can_handle_valid_pyproject(pyproject_file: Path):
    spec = PyProjectTomlSpec(str(pyproject_file))
    assert spec.can_handle() is True


def test_can_handle_invalid_pyproject(tmp_path: Path):
    with open(file := tmp_path / 'setup.py', 'w') as f:
        f.write("invalid content")
    spec = PyProjectTomlSpec(str(file))
    assert spec.can_handle() is False


def test_can_handle_missing_file(tmp_path: Path):
    spec = PyProjectTomlSpec(str(tmp_path / "does-not-exist.toml"))
    with pytest.raises(FileNotFoundError):
        spec.can_handle()


def test_env_includes_python_and_dependencies(pyproject_file: Path):
    spec = PyProjectTomlSpec(str(pyproject_file))
    env = spec.env
    names = {pkg.name for pkg in env.requested_packages}
    assert "python" in names
    assert "numpy" in names
    assert "requests" in names
    assert "pytest" in names
    if sys.platform == 'win32':
        assert "pywin32" in names
    if sys.platform == 'darwin':
        assert "some-osx-package" in names
