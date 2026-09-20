# conda-pyproject-toml

![PyPI Version](https://img.shields.io/pypi/v/conda-pyproject-toml)
![Conda Version](https://img.shields.io/conda/vn/conda-forge/conda-pyproject-toml)

[Conda](https://docs.conda.io) plugin that installs dependencies from a pyproject.toml file.

## Installation

```shell
conda install -c conda-forge conda-pyproject-toml
```

> [!NOTE]
> Altough the package is [uploaded to PyPI](https://pypi.org/project/conda-pyproject-toml/), it cannot be installed using `pip` directly due to [a missing recent version of `conda`](https://pypi.org/project/conda/) on [PyPI](https://pypi.org).

## Usage

Once installed, the plugin adds support for installing dependencies from a `pyproject.toml` file.

* Install requirements into current environment

  `conda install --file pyproject.toml`

* Create a new environment

  `conda create --name my-conda-environment --file pyproject.toml`

## Development

See [CONTRIBUTING](CONTRIBUTING.md)
