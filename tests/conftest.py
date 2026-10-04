import os

os.environ['CONDA_TEST_SOLVERS'] = 'classic,libmamba,rattler'
pytest_plugins = "conda.testing.fixtures"
