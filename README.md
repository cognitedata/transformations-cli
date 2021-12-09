<a href="https://cognite.com/">
    <img src="https://github.com/cognitedata/cognite-python-docs/blob/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />
</a>

Cognite Python `transformations-cli`
================================
[![Build Status](https://github.com/cognitedata/transformations-cli/workflows/release/badge.svg)](https://github.com/cognitedata/transformations-cli/actions)
[![Documentation Status](https://readthedocs.com/projects/cognite-transformations-cli/badge/?version=latest)](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/cognitedata/transformations-cli/branch/main/graph/badge.svg?token=PSkli74vvX)](https://codecov.io/gh/cognitedata/transformations-cli)
[![PyPI version](https://badge.fury.io/py/cognite-transformations-cli.svg)](https://pypi.org/project/cognite-transformations-cli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cognite-transformations-cli)
[![License](https://img.shields.io/github/license/cognitedata/python-extractor-utils)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Transformations CLI

The Transormations CLI is a replacement for [jetfire-cli](https://github.com/cognitedata/jetfire-cli) rewritten on top
of the new Python SDK for Transformations.

### CLI Documentation

Documentation for CLI is hosted [here](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/).

### GitHub Action

`transformations-cli` also provides a GitHub Action which can be used to deploy transformations. You can find the documentation for transformations-cli GitHub Action [here](githubaction.md).


### GitHub Action Migration: jetfire-cli@v2 to transformations-cli@main

If you've already used the old `jetfire-cli` in a GitHub Action we recommend you migrate to the new GitHub Action. You can find the migration guide [here](migrationguide.md).

### Contributing

We use [poetry](https://python-poetry.org) to manage dependencies and to administrate virtual environments. To develop
`transformations-cli`, follow the following steps to set up your local environment:

 1. Install poetry: (add `--user` if desirable)
    ```
    $ pip install poetry
    ```
 2. Clone repository:
    ```
    $ git clone git@github.com:cognitedata/transformations-cli.git
    ```
 3. Move into the newly created local repository:
    ```
    $ cd transformations-cli
    ```
 4. Create virtual environment and install dependencies:
    ```
    $ poetry install
    ```

All code must pass [black](https://github.com/ambv/black) and [isort](https://github.com/timothycrosley/isort) style
checks to be merged. It is recommended to install pre-commit hooks to ensure this locally before commiting code:

```
$ poetry run pre-commit install
```

To publish a new version change the version in `cognite/transformations_cli/__init__.py` and `pyproject.toml`. Also, remember to add an entry to `CHANGELOG`.

This project adheres to the [Contributor Covenant v2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)
as a code of conduct.


