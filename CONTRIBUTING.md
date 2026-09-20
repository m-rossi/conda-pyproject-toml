# Contributing

## Download

Make a fork of the main [`conda-pyproject-toml` repository](https://github.com/m-rossi/conda-pyproject-toml) and clone the fork

```sh
git clone https://github.com/<your-github-username>/conda-pyproject-toml
```

Contributions to `conda-pyproject-toml` can then be made by submitting pull requests on GitHub.

## Install

To install all necessary dependencies install a recent version of the plugin via `conda`

```shell
conda install -c conda-forge conda-pyproject-toml
```

Then switch to the folder of your fork and install the dependencies:

```sh
cd conda-pyproject-toml
conda install --file pyproject.toml
```

Last step: Install the package in _editable_ mode by executing

```sh
pip install --no-deps -e .
```

## Test

Test the package with [pytest](https://docs.pytest.org) by executing

```sh
pytest .
```

## Build

This package follows the [packaing guide](https://packaging.python.org/tutorials/packaging-projects/) and you can create new packages for [PyPI](https://pypi.org/) by executing.

```sh
python -m build --sdist
```
