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
-----

Authenticate with API keys
--------------------------

To use transformations-cli:
    - The ``TRANSFORMATIONS_API_KEY`` environment variable must be set to a valid API key for a service account which has access to Transformations. 
    - ``TRANSFORMATIONS_PROJECT`` environment variable is optional for API key authentication, CDF project can be inferred from API key if skipped. 

Authenticate with OIDC credentials
----------------------------------

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
   :widths: 25 15 100 15
   :header-rows: 1

   * - Command
     - Args
     - Options
     - Description
   * - list
     - 
     - ``--limit``
     - List transformations
   * - show
     - 
     - ``--external-id``, ``--id``, ``--job-id``
     - Show a transformation/job
   * - jobs
     - 
     - ``--external-id``, ``--id``, ``--limit``
     - List jobs
   * - delete
     - 
     - ``--external-id``, ``--id``, ``--delete-schedule``
     - Delete a transformation
   * - query
     - ``query``
     - ``--source-limit``, ``--infer-schema-limit``, ``--limit``
     - Run a query
   * - run
     - 
     - ``--external-id``, ``--id``, ``--watch``, ``--watch-only``, ``--time-out``
     - Run a transformation
   * - deploy
     - ``path``
     - 
     - Deploy transformations

``help``
--------
.. code-block:: bash

    transformations-cli --help
    transformations-cli <subcommand> --help

``transformations-cli list``
----------------------------

``transformations-cli show``
----------------------------
``transformations-cli show`` can show the details of a transformation and/or a transformatin job.
At minimum, this command requires either an ``--id`` or ``--external-id`` or ``--job-id`` to be specified:

.. code-block:: bash

    transformations-cli show --id=1234
    transformations-cli show --external-id=my-transformation
    transformations-cli show --job-id=1
    transformations-cli show --external-id=my-transformation --job-id=1

It prints the transformation details in a tabular format, such as latest job's metrics and notifications.

``transformations-cli jobs``
----------------------------
``transformations-cli jobs`` can list the latest jobs. 
You can optionally provide the ``external_id`` or ``id`` of the transformations of which jobs you want to list. 
You can also provide ``--limit``, which defaults to 10. Use ``--limit=-1`` if you want to list all.

.. code-block:: bash

    transformations-cli jobs
    transformations-cli jobs --limit=2
    transformations-cli jobs --id=1234
    transformations-cli jobs --external-id=my-transformation

``transformations-cli delete``
------------------------------
``transformations-cli`` provides a delete subcommand, which can delete a transformation. 

At minimum, this command requires either an ``--id`` or ``--external-id`` to be specified:

.. code-block:: bash

    transformations-cli delete --id=1234
    transformations-cli delete --external-id=my-transformation

You can also specify ``--delete-schedule`` flag to delete a scheduled transformation.

.. code-block:: bash

    transformations-cli delete --id=1234 --delete-schedule

Make a query: ``transformations-cli query``
-------------------------------------------

Start a transformation job: ``transformations-cli run``
-------------------------------------------------------
``transformations-cli run`` can start transformation jobs and/or wait for jobs to complete.

At minimum, this command requires either an ``--id`` or ``--external-id`` to be specified:

.. code-block:: bash

    transformations-cli run --id=1234
    transformations-cli run --external-id=my-transformation

Without any additional arguments, this command will start a transformation job, and exit immediately. If you want wait for the job to complete, use the ``--watch`` option:

.. code-block:: bash

    transformations-cli run --id=1234 --watch

When using the ``--watch`` option, transformation-cli will return a non-zero exit code if the transformation job failed, or if it did not finish within a given timeout (which is 12 hours by default). This timeout can be configured using the ``--time-out`` option.

If you want to watch a job for completion without actually starting a transformation job, specify ``--watch-only`` instead of ``--watch``. This will watch the most recently started job for completion.

Create or update transformations: ``transformations-cli deploy``
----------------------------------------------------------------

``Github Action``
-----------------