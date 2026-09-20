import re
import sys
import warnings
from pathlib import Path

from conda import plugins
from conda.base.context import context
from conda.models.environment import Environment
from conda.models.match_spec import MatchSpec
from conda.plugins.types import EnvironmentSpecBase
from grayskull.base.track_packages import solve_pkg_name
from grayskull.strategy.py_toml import get_all_toml_info
from grayskull.strategy.pypi import PYPI_CONFIG

from .exceptions import SolverWarning


class PyProjectTomlSpec(EnvironmentSpecBase):
    extensions = {'.toml'}

    def __init__(self, filename: str):
        self.filename = filename

    def can_handle(self) -> bool:
        """Determines if the EnvSpec plugin can read and operate on the environment described by
        the `filename`.

        Returns
        -------
        bool
            True, if the plugin can interpret the file.
        """
        if self.filename is None or not Path(self.filename).exists():
            raise FileNotFoundError
        if Path(self.filename).name == 'pyproject.toml':
            return True
        else:
            return False

    def parse_requirement(self, requirement: str, solver: str) -> MatchSpec | None:
        """Parses a requirement string and returns a MatchSpec object if applicable.

        Parameters
        ----------
        requirement : str
            The requirement string to parse.

        solver : str
            The solver being used.

        Returns
        -------
        conda.models.match_spec.MatchSpec | None
            The parsed MatchSpec object, or None if the requirement is not applicable.
        """
        requirement = requirement.strip()
        if ';' in requirement:
            parts = requirement.split(';')
            if len(parts) != 2:
                raise ValueError(f"Invalid requirement format: {requirement}")
            requirement = parts[0].strip()
            environment = parts[1].strip()
            parts = re.split(r'(>=|<=|==|!=|>|<)', environment)
            if len(parts) != 3:
                raise ValueError(f"Invalid environment marker format: {environment}")
            marker = parts[0].strip()
            comparison = parts[1].strip()
            value = parts[2].strip().replace("'", "").replace('"', '')
            match marker:
                case 'sys_platform':
                    if value == sys.platform:
                        environment = ''
                    else:
                        return None
                case 'python_version':
                    environment = f'[when=python{comparison}{value}]'
                    if solver != 'rattler':
                        warnings.warn(
                            'Environment marker regarding Python version for requirement '
                            '"{requirement}" found. These markers are not yet supported in all '
                            'solvers, so this requirement may be installed although not required.'
                            ' See https://github.com/conda/conda/issues/16073 for progress of '
                            'this feature.',
                            category=SolverWarning,
                        )
                case _:
                    raise ValueError(f"Unsupported environment marker: {marker}")
        else:
            environment = ''
        requirement = solve_pkg_name(requirement, PYPI_CONFIG)
        return MatchSpec(f'{requirement}{environment}')

    @property
    def env(self) -> Environment:
        """Express the provided environment file as a conda environment object.

        Returns
        -------
        conda.models.environment.Environment
            the conda environment represented by the file.
        """
        metadata = get_all_toml_info(self.filename)
        requirements = []
        for section in ['host', 'run']:
            for requirement in metadata['requirements'][section]:
                requirements.append(requirement)
        for extra in metadata['requirements']['extra']:
            for requirement in metadata['requirements']['extra'][extra]:
                requirements.append(requirement)
        requested_packages = []
        for requirement in requirements:
            if (parsed_requirement := self.parse_requirement(requirement, solver=context.solver)):
                requested_packages.append(parsed_requirement)
        return Environment(
            platform=context.subdir,
            name='pyproject-toml-environment',
            requested_packages=requested_packages,
        )


@plugins.hookimpl
def conda_environment_specifiers():
    yield plugins.CondaEnvironmentSpecifier(
        name='pyproject-toml',
        environment_spec=PyProjectTomlSpec,
        aliases=('pyproject', 'toml'),
    )
