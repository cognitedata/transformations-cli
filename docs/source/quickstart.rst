.. quickstart:

Quickstart
==========


Installation
------------

To install this package:

.. code-block:: bash

   pip install cognite-transformations-cli

If the Cognite SDK is not already installed, the installation will automatically fetch and install it as well.

Usage
------------

Authenticate with API keys
------------

To use transformations-cli:
    - The ``TRANSFORMATIONS_API_KEY`` environment variable must be set to a valid API key for a service account which has access to Transformations. 
    - ``TRANSFORMATIONS_PROJECT`` environment variable is optional for API key authentication, CDF project can be inferred from API key if skipped. 

Authenticate with OIDC credentials
------------

When using OIDC, you need to set the environment variables:
    - ``TRANSFORMATIONS_CLIENT_ID``: Required
    - ``TRANSFORMATIONS_CLIENT_SECRET``: Required
    - ``TRANSFORMATIONS_TOKEN_URL``: Required
    - ``TRANSFORMATIONS_PROJECT``: Required
    - ``TRANSFORMATIONS_SCOPES``: Transformations CLI assumes that this is optional, generally required to authenticate except for Aize project. Space separated for multiple scopes.
    - ``TRANSFORMATIONS_AUDIENCE``: Optional

By default, transformations-cli runs against the main CDF cluster (europe-west1-1). To use a different cluster, specify the ``--cluster`` parameter or set the environment variable ``TRANSFORMATIONS_CLUSTER``. Note that this is a global parameter, which must be specified before the subcommand. For example:

.. code-block:: bash

    transformations-cli --cluster=greenfield <subcommand> [...args]


.. list-table:: Transformations CLI Commands
   :widths: 25 25 100
   :header-rows: 1

   * - Command
     - Args
     - Options
   * - deploy
     - ``path``
     - 
   * - list
     - 
     - ``--limit``
   * - show
     - 
     - ``--external-id``, ``--id``, ``--job-id``
   * - jobs
     - 
     - ``--external-id``, ``--id``, ``--limit``
   * - delete
     - 
     - ``--external-id``, ``--id``
   * - query
     - ``query``
     - ``--source-limit``, ``--infer-schema-limit``, ``--limit``
   * - run
     - 
     - ``--external-id``, ``--id``, ``--watch``, ``--watch-only``

``transformations-cli deploy``
-----------------------------------

``transformations-cli list``
-------------------------------------

``transformations-cli show``
-------------------------------------

``transformations-cli jobs``
-------------------------------------

``transformations-cli delete``
-------------------------------------

``transformations-cli query``
-------------------------------------

``transformations-cli run``
-------------------------------------

``Github Action``
-------------------------------------