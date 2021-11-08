<a href="https://cognite.com/">
    <img src="https://github.com/cognitedata/cognite-python-docs/blob/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />
</a>

Cognite Python `transformations-cli`
================================
[![Build Status](https://github.com/cognitedata/transformations-cli/workflows/release/badge.svg)](https://github.com/cognitedata/transformations-cli/actions)
[![codecov](https://codecov.io/gh/cognitedata/transformations-cli/branch/master/graph/badge.svg?token=7AmVCpAh7I)](https://codecov.io/gh/cognitedata/transformations-cli)
[![PyPI version](https://badge.fury.io/py/cognite-transformations-cli.svg)](https://pypi.org/project/cognite-transformations-cli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cognite-transformations-cli)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Transformations CLI

The Transormations CLI is a replacement for [jetfire-cli](https://github.com/cognitedata/jetfire-cli) rewritten on top
of the new Python SDK for Transformations.

Documentation is hosted [here](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/).

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

This project adheres to the [Contributor Covenant v2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)
as a code of conduct.


