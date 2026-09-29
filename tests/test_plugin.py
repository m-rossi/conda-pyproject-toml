import sys
from pathlib import Path
from uuid import uuid4

import pytest
from conda.testing.fixtures import CondaCLIFixture
from conda.testing.integration import package_is_installed

from conda_pyproject_toml import PyProjectTomlSpec
from conda_pyproject_toml.exceptions import SolverWarning

PYPROJECT_CONTENT = """
[project]
name = "example-project"
requires-python = ">=3.10"
dependencies = [
  "numpy>=1.26",
  "requests==2.31.0",
  "tomli>=2.4.1; python_version < '3.11'",
  "pywin32>=312; sys_platform == 'win32'",
  "mlx>=0.32; sys_platform == 'darwin'",
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
        f.write('invalid content')
    spec = PyProjectTomlSpec(str(file))
    assert spec.can_handle() is False


def test_can_handle_missing_file(tmp_path: Path):
    spec = PyProjectTomlSpec(str(tmp_path / 'does-not-exist.toml'))
    with pytest.raises(FileNotFoundError):
        spec.can_handle()


def test_env_includes_python_and_dependencies(pyproject_file: Path):
    spec = PyProjectTomlSpec(str(pyproject_file))
    env = spec.env
    names = {pkg.name for pkg in env.requested_packages}
    assert 'python' in names
    assert 'numpy' in names
    assert 'requests' in names
    assert 'pytest' in names
    if sys.platform == 'win32':
        assert 'pywin32' in names
    else:
        assert 'pywin32' not in names
    if sys.platform == 'darwin':
        assert 'mlx' in names
    else:
        assert 'mlx' not in names


@pytest.mark.parametrize("solver", ["classic", "libmamba", "rattler"])
def test_cli(
    conda_cli: CondaCLIFixture,
    tmp_envs_dir: Path,
    pyproject_file: Path,
    solver: str,
):
    env_name = uuid4().hex[:8]
    prefix = tmp_envs_dir / env_name

    conda_args = (
        'env',
        'create',
        '--name', env_name,
        '--file', str(pyproject_file),
        '--solver', solver,
    )
    if solver == 'rattler':
        conda_cli(*conda_args)
    else:
        with pytest.warns(SolverWarning):
            conda_cli(*conda_args)
    assert prefix.exists()
    assert package_is_installed(prefix, 'python')
    assert package_is_installed(prefix, 'numpy')
    assert package_is_installed(prefix, 'requests')
    assert package_is_installed(prefix, 'pytest')
    if sys.platform == 'win32':
        assert package_is_installed(prefix, 'pywin32')
    else:
        assert not package_is_installed(prefix, 'pywin32')
    if sys.platform == 'darwin':
        assert package_is_installed(prefix, 'mlx')
    else:
        assert not package_is_installed(prefix, 'mlx')
