<a href="https://cognite.com/">
    <img src="https://github.com/cognitedata/cognite-python-docs/blob/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />
</a>

Cognite Python `transformations-cli`
================================
[![Build Status](https://github.com/cognitedata/transformations-cli/workflows/release/badge.svg)](https://github.com/cognitedata/transformations-cli/actions)
[![Documentation Status](https://readthedocs.com/projects/cognite-transformations-cli/badge/?version=latest&token=a9bab88214cbf624706005f6a71bbd77964efc910f8e527c7b3d75edc016397c)](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/?badge=latest)
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

### Github Action

`transformations-cli` also provides a GitHub Action, which can be used to deploy transformations.

1- Create transformation manifests and place them into a folder structure in your repository.

#### Transformation Manifests

Important notes:
- When a scheduled transformations represented in a manifest without schedule provided, deploy will delete the existing schedule.

- When an existing notification is not provided along with the transformation to be updated, notification will be deleted.

- Values specified as `${VALUE}` are treated as environment variables while `VALUE` is directly used as the actual value.

- Old jetfire-cli style manifests can be used by adding `legacy: true` inside the old manifest.

- The manifest directory is scanned recursively for `*.yml` and `*.yaml` files, so you can organize your transformations into separate subdirectories.

##### Manifest with API keys

```yaml
   externalId: "test-cli-transform"
   name: "test-cli-transform"
   destination: 
   type: "assets"
   shared: True
   action: "upsert"
   query: "select 'asd' as name, 'asd' as externalId"
   # query:
   #   file: query.sql
   schedule: "* * * * *"
   ignoreNullFields: False
   notifications:
   - emel.varol@cognite.com
   authentication:
   apiKey: ${API_KEY}

   # # If you need to specity read/write authentication separately
   # authentication:
   #   read:
   #     apiKey: ${API_KEY}
   #   write:
   #     apiKey: ${API_KEY}
```

##### Manifest with OIDC Credentials

```yaml
# Required
externalId: "test-cli-transform-oidc"
# Required
name: "test-cli-transform-oidc"

# Required
# Valid values are: "assets", "timeseries", "asset_hierarchy", events", "datapoints", 
# "string_datapoints", "sequences", "files", "labels", "relationships", "raw", "data_sets"
destination: 
  type: "assets"
# When writing to RAW tables, use the following syntax:
# destination:
#   type: raw
#   rawDatabase: some_database
#   rawTable: some_table

# Optional, default: True
shared: True

# Optional, default: upsert
# Valid values are:
#   upsert: Create new items, or update existing items if their id or externalId
#           already exists.
#   create: Create new items. The transformation will fail if there are id or
#           externalId conflicts.
#   update: Update existing items. The transformation will fail if an id or 
#           externalId does not exist.
#   delete: Delete items by internal id.
action: "upsert"

# Required
query: "select 'asd' as name, 'asd' as externalId"

# Or the path to a file containing the SQL query for this transformation.
# query:
#   file: query.sql

# Optional, default: null
# If null, the transformation will not be scheduled.
schedule: "* * * * *"
ignoreNullFields: False

# Optional, default: null
# List of email adresses to send emails to on transformation errors
notifications:
  - example@cognite.com

# The client credentials to be used in the transformation
authentication:
  clientId: ${CLIENT_ID}
  clientSecret: ${CLIENT_SECRET}
  tokenUrl: ${TOKEN_URL}
  scopes: 
    - ${SCOPES}
  cdfProjectName: ${CDF_PROJECT_NAME}
  # audience: ""

# If you need to specity read/write credentials separately
# authentication:
#   read:
#     clientId: ${CLIENT_ID}
#     clientSecret: ${CLIENT_SECRET}
#     tokenUrl: ${TOKEN_URL}
#     scopes: 
#       - ${SCOPES}
#     cdfProjectName: ${CDF_PROJECT_NAME}
#     # audience: ""
#   write:
#     clientId: ${CLIENT_ID}
#     clientSecret: ${CLIENT_SECRET}
#     tokenUrl: ${TOKEN_URL}
#     scopes: 
#       - ${SCOPES}
#     cdfProjectName: ${CDF_PROJECT_NAME}
#     # audience: ""
```

2- To deploy a set of transformations in a GitHub workflow, add a step which references the action in your job.

#### Deploy step with API keys

```yaml
- name: Deploy transformations
  uses: cognitedata/transformations-cli@main
  with:
    path: transformations # Transformation manifest folder, relative to github root dir
    api-key: ${{ secrets.TRANSFORMATIONS_API_KEY }}
    # If not using the main europe-west1-1 cluster:
    # cluster: greenfield
    # cdf-project-name: my-project # to supress python sdk warning, it is not required for API keys.
  env:
    # API key to be used when running your transformations,
    # As referenced in your transformation manifests
    SOME_API_KEY: ${{ secrets.SOME_API_KEY }}
```

This GitHub action takes the following inputs:

| Name      | Description |
|-----------|-------------|
| `path`    | _(Required)_ The path to a directory containing transformation manifests. This is relative to `$GITHUB_WORKSPACE`, which will be the root of the repository when using [actions/checkout](https://github.com/actions/checkout) with default settings. |
| `api-key` | _(Required)_ The API key used for authenticating with transformations. Equivalent to setting the `TRANSFORMATIONS_API_KEY` environment variable. |
| `cluster` | _(Optional)_ The name of the cluster where Transformations is hosted. Equivalent to setting the `TRANSFORMATIONS_CLUSTER` environment variable. |

Additionally, you must specify environment variables for any API keys referenced in transformation manifests.

#### Deploy step with OIDC credentials

Alternatively when using OIDC, the action needs the client details instead of `api-key`:
```yaml
- name: Deploy transformations
  uses: cognitedata/transformations-cli@main
  env:
      # Credentials to be used when running your transformations,
      # as referenced in your manifests:
      COGNITE_CLIENT_ID: my-cognite-client-id
      COGNITE_CLIENT_SECRET: ${{ secrets.cognite_client_secret }}
  with:
      # Credentials used for deployment
      path: transformations  # Transformation manifest folder, relative to github root dir
      client-id: my-jetfire-client-id
      client-secret: ${{ secrets.jetfire_client_secret] }}
      token-url: https://login.microsoftonline.com/<my-azure-tenant-id>/oauth2/v2.0/token
      cdf-project-name: my-project-name
      # If you need to provide multiple scopes, the format: "scope1 scope2 scope3"
      scopes: https://<my-cluster>.cognitedata.com/.default
      # audience: "" # Optional
```

This GitHub action takes the following inputs:

| Name      | Description |
|-----------|-------------|
| `path`    | _(Required)_ The path to a directory containing transformation manifests. This is relative to `$GITHUB_WORKSPACE`, which will be the root of the repository when using [actions/checkout](https://github.com/actions/checkout) with default settings. |
| `client-id` | _(Required)_ The CLIENT ID used for authenticating with transformations. Equivalent to setting the `TRANSFORMATIONS_CLIENT_ID` environment variable. |
| `client-secret` | _(Required)_ The CLIENT SECRET used for authenticating with transformations. Equivalent to setting the `TRANSFORMATIONS_CLIENT_SECRET` environment variable. |
| `token-url` | _(Required)_ The TOKEN URL used for requesting token to authenticate with transformations. Equivalent to setting the `TRANSFORMATIONS_TOKEN_URL` environment variable. |
| `cdf-project-name` | _(Required)_ Equivalent to setting the `TRANSFORMATIONS_PROJECT` environment variable. |
| `scopes` | _(Optional)_ The SCOPES used for authenticating with transformations. Equivalent to setting the `TRANSFORMATIONS_SCOPES` environment variable. Space separated if multiple needed. |
| `audience` | _(Optional)_ The AUDIENCE used for authenticating with transformations. Equivalent to setting the `TRANSFORMATIONS_AUDIENCE` environment variable. |
| `cluster` | _(Optional)_ The name of the cluster where Transformations is hosted. Equivalent to setting the `TRANSFORMATIONS_CLUSTER` environment variable. |



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

To publish a new version, change the version in `cognite/transformations_cli/__init__.py` and `pyproject.toml`. Also, remember to add an entry to `CHANGELOG`.

This project adheres to the [Contributor Covenant v2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)
as a code of conduct.


