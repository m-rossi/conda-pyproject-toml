import sys
from pathlib import Path

import pytest
from conda.base.context import context
from conda.testing.fixtures import CondaCLIFixture, TmpEnvFixture
from conda.testing.integration import package_is_installed

from conda_pyproject_toml import PyProjectTomlSpec
from conda_pyproject_toml.exceptions import SolverWarning

pytestmark = [
    pytest.mark.usefixtures('parametrized_solver_fixture'),
]

PYPROJECT_CONTENT = """
[project]
name = "example-project"
requires-python = ">=3.10"
dependencies = [
  "numpy>=1.26",
  "requests==2.31.0",
  "scipy ; python_version < '3.14'",
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


@pytest.mark.parametrize('python_version', [12, 13, 14])
def test_cli(
    conda_cli: CondaCLIFixture,
    tmp_env: TmpEnvFixture,
    pyproject_file: Path,
    python_version: int,
):
    with tmp_env(f'python=3.{python_version}') as prefix:
        conda_args = (
            'install',
            '--prefix', prefix,
            '--file', str(pyproject_file),
            '--yes',
        )
        if context.solver == 'rattler':
            conda_cli(*conda_args)
        else:
            with pytest.warns(SolverWarning):
                conda_cli(*conda_args)
        assert prefix.exists()
        assert package_is_installed(prefix, 'python')
        assert package_is_installed(prefix, 'numpy')
        assert package_is_installed(prefix, 'requests')
        assert package_is_installed(prefix, 'pytest')
        if python_version >= 14 and context.solver == 'rattler':
            assert not package_is_installed(prefix, 'scipy')
        else:
            assert package_is_installed(prefix, 'scipy')
        if sys.platform == 'win32':
            assert package_is_installed(prefix, 'pywin32')
        else:
            assert not package_is_installed(prefix, 'pywin32')
        if sys.platform == 'darwin':
            assert package_is_installed(prefix, 'mlx')
        else:
            assert not package_is_installed(prefix, 'mlx')
