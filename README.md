# Cognite Transformations CLI

[![Build Status](https://github.com/cognitedata/transformations-cli/workflows/release/badge.svg)](https://github.com/cognitedata/transformations-cli/actions)
[![Documentation Status](https://readthedocs.com/projects/cognite-transformations-cli/badge/?version=latest)](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/cognitedata/transformations-cli/branch/main/graph/badge.svg?token=PSkli74vvX)](https://codecov.io/gh/cognitedata/transformations-cli)
[![PyPI version](https://badge.fury.io/py/cognite-transformations-cli.svg)](https://pypi.org/project/cognite-transformations-cli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cognite-transformations-cli)
[![License](https://img.shields.io/github/license/cognitedata/python-extractor-utils)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Transformations CLI

Use the Transformations command-line interface (**Transformations CLI**) to manage the lifecycle of your transformation jobs using the command line. With the Transformations CLI, you can process data from the CDF staging area (RAW) into the CDF data model. To learn more about how the Cognite Transformations CLI package works, see the **documentation** [here](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/)

The **Transformations CLI** is based on Python and replaces the [Jetfire CLI](https://github.com/cognitedata/jetfire-cli).

### GitHub Action

The **Transformations CLI** provides a GitHub Action to deploy transformations. You'll find the documentation [here](githubaction.md).

We've also created a **CI/CD template** that uses GitHub Workflows. You'll find the documentation [here](https://github.com/cognitedata/transformations-action-template).

### Using Transformations CLI in Azure Pipelines

We publish `transformations-cli` docker images in [dockerhub](https://hub.docker.com/r/cognite/transformations-cli/tags) for every version released. The images tagged as `cognite/transformations-cli:<version>-azure` can be used in Azure Pipelines (See an example tag [here](https://hub.docker.com/layers/transformations-cli/cognite/transformations-cli/2.1.1-azure/images/sha256-310aa01bcfc4f379c82076cc0386cc401ed1565d3ce4a2d8c3235d7061428145?context=explore)). We suggest you check [the example Azure Pipeline workflow configuration](azure_pipelines_example/azure-pipelines.yaml) and [the corresponding transformation manifest](azure_pipelines_example/transformations/manifest.yaml).

### Migrating from Jetfire CLI

**Transformations CLI** replaces the [Jetfire CLI](https://github.com/cognitedata/jetfire-cli). If you've already used the **Jetfire CLI** in a GitHub Action, we recommend migrating to the **Transformations CLI** GitHub Action. You'll find the migration guide [here](migrationguide.md).

### Contributing

We use [poetry](https://python-poetry.org) to manage dependencies and to administrate virtual environments. To develop
**Transformations CLI**, follow these steps to set up your local environment:

1.  Install poetry: (add `--user` if desirable)
    ```
    $ pip install poetry
    ```
2.  Clone repository:
    ```
    $ git clone git@github.com:cognitedata/transformations-cli.git
    ```
3.  Move into the newly created local repository:
    ```
    $ cd transformations-cli
    ```
4.  Create a virtual environment and install dependencies:

    ```
    $ poetry install
    ```

5.  All the code must pass [black](https://github.com/ambv/black) and [isort](https://github.com/timothycrosley/isort) style
    checks before it can be merged. We recommend installing pre-commit hooks to ensure this locally before you commit your code:

```
$ poetry run pre-commit install
```

6. To run tests:
```
$ poetry run pytest
$ poetry run pytest <test file path>
$ poetry run pytest <test file path>::<test function name>
```

7. To publish a new version, change the version in `cognite/transformations_cli/__init__.py` and `pyproject.toml`. Make sure to update the `CHANGELOG`.

This project adheres to the [Contributor Covenant v2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)
as a code of conduct.

