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
^^^^^^^^^^^^^^^^^^^^^^^^^^^
To use transformations-cli:
    - The ``TRANSFORMATIONS_API_KEY`` environment variable must be set to a valid API key for a service account which has access to Transformations. 
    - ``TRANSFORMATIONS_PROJECT`` environment variable is optional for API key authentication, CDF project can be inferred from API key if skipped. 

Authenticate with OIDC credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
     - ``--limit``, ``--interactive``
     - List transformations
   * - show
     - 
     - ``--external-id``, ``--id``, ``--job-id``
     - Show a transformation/job
   * - jobs
     - 
     - ``--external-id``, ``--id``, ``--limit``, ``--interactive``
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
     - ``path``, ``--debug``
     - 
     - Deploy transformations

Help
--------
.. code-block:: bash

    transformations-cli --help
    transformations-cli <subcommand> --help

``transformations-cli list``
----------------------------
``transformations-cli list`` can list transformations in a CDF project. ``--limit`` option is used to change number of transformations to list, defaults to 10.

.. code-block:: bash

    transformations-cli list
    transformations-cli list --limit=2

It prints transformations details in a tabular format.

.. list-table:: List options
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Option
     - Default
     - Flag
     - Required
     - Description
   * - ``--limit``
     - 10
     - No
     - No
     - Number of transformations to list. Use -1 to list all.
   * - ``--interactive``
     - False
     - Yes
     - No
     - Show 10 transformations at a time, waiting for keypress to display next batch.


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

.. list-table:: Show options
   :widths: 25 25 25 25
   :header-rows: 1

   * - Option
     - Flag
     - Required
     - Description
   * - ``--id``
     - No
     - No
     - The ``id`` of the transformation to show. Either this or ``--external-id`` must be specified if ``job-id`` not specified.
   * - ``--external-id``
     - No
     - No
     - The ```external_id``` of the transformation to show. Either this or ``--id`` must be specified if ``job-id`` not specified.
   * - ``--job-id``
     - No
     - No
     - The id of the job to show. Include this to show job details.


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


.. list-table:: Jobs options
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Option
     - Default
     - Flag
     - Required
     - Description
   * - ``--limit``
     - 10
     - No
     - No
     - Limit for the job history. Use -1 to retrieve all results.
   * - ``--id``
     - 
     - No
     - No
     - List jobs by transformation ``id``. Either this or ``--external-id`` must be specified.
   * - ``--external-id``
     - 
     - No
     - No
     - List jobs by transformation ``external_id``. Either this or ``--id`` must be specified.
   * - ``--interactive``
     - False
     - Yes
     - No
     - Show 10 jobs at a time, waiting for keypress to display next batch.

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


.. list-table:: Delete options
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Option
     - Default
     - Flag
     - Required
     - Description
   * - ``--id``
     - 
     - No
     - No
     - ``id`` of the transformation to be deleted. Either this or ``--external-id`` must be specified.
   * - ``--external-id``
     - 
     - No
     - No
     - ``external_id`` of the transformation to be deleted. Either this or ``--id`` must be specified.
   * - ``--delete-schedule``
     - False
     - Yes
     - No
     - Scheduled transformations cannot be deleted, delete schedule along with the transformation.

Make a query: ``transformations-cli query``
-------------------------------------------
transformations-cli also allows you to run queries.

.. code-block:: bash

    transformations-cli query "select * from _cdf.assets limit 100"

This will print the schema and the results. 
The query command is intended for previewing your SQL queries, and is not designed for large data exports. For this reason, there are a few limits in place. Query command takes ``--infer-schema-limit``, ``--source-limit`` and ``--limit`` options. Default values are 100, 100 and 1000 in the corresponding order.


.. list-table:: Query args
   :widths: 25 25 25
   :header-rows: 1

   * - Arg
     - Required
     - Description
   * - ``query``
     - Yes
     - SQL query to preview, string.

.. list-table:: Query options
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Option
     - Default
     - Flag
     - Required
     - Description
   * - ``--limit``
     - 1000
     - No
     - No
     - This is equivalent to a final LIMIT clause on your query.
   * - ``--source-limit``
     - 100
     - No
     - No
     - This limits the number of rows to read from each data source.
   * - ``--infer-schema-limit``
     - 100
     - No
     - No
     - Schema inference limit.

More details on ``source limit`` and ``infer schema limit``:
    - ``--source-limit``: For example, if the source limit is 100, and you take the UNION of two tables, you will get 200 rows back. This parameter is set to 100 by default, but you can remove this limit by setting it to -1.
    - ``--infer-schema-limit``: As RAW tables have no predefined schema, we need to read some number of rows to infer the schema of the table. As with the source limit, this is set to 100 by default, and can be made unlimited by setting it to -1. If your RAW data is not properly being split into separate columns, you should try to increase or remove this limit.

.. code-block:: bash

    transformations-cli query --source-limit=-1 "select * from db.table"


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


.. list-table:: Run options
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Option
     - Default
     - Flag
     - Required
     - Description
   * - ``--id``
     - 
     - No
     - No
     - The ``id`` of the transformation to run. Either this or ``--external-id`` must be specified.
   * - ``--external-id``
     - 
     - No
     - No
     - The ``external_id`` of the transformation to run. Either thisor ``--id`` must be specified.
   * - ``--watch``
     - False
     - Yes
     - No
     - Wait until job has completed.
   * - ``--watch-only``
     - False
     - Yes
     - No
     - Do not start a transformation job, only watch the most recent job for completion.
   * - ``--time-out``
     - 12 hr (in secs)
     - No
     - No
     - Maximum amount of time to wait for job to complete in seconds.

Deploy transformations: ``transformations-cli deploy``
----------------------------------------------------------------
``transformations-cli deploy`` is used to create or update transformations described by manifests.

The primary purpose of transformations-cli is to support continuous delivery, allowing you to manage transformations in a version control system:
    - Transformations are described by YAML files, whose structure is described further below in this document.
    - It is recommended to place these manifest files in their own directory, to avoid conflicts with other files.

To deploy a set of transformations, use the deploy subcommand:

.. code-block:: bash

    transformations-cli deploy <path>

The ``<path>`` argument should point to a directory containing YAML manifests. 
This directory is scanned recursively for ``*.yml`` and ``*.yaml`` files, so you can organize your transformations into separate subdirectories.

.. list-table:: Deploy args
   :widths: 25 25 25 25
   :header-rows: 1

   * - Arg
     - Default
     - Required
     - Description
   * - ``path``
     - .
     - Yes
     - Root folder of transformation manifests. 

.. list-table:: Debug options
   :widths: 25 25 25 25 25
   :header-rows: 1

   * - Option
     - Default
     - Flag
     - Required
     - Description
   * - ``--debug``
     - Yes
     - No
     - No
     - Print `external_id``s for the upserted resources besides the counts.

``Transformation Manifest``
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Important notes:
    - When a scheduled transformation is represented in a manifest without ``schedule`` provided, deploy will delete the existing schedule.
    - When an existing notification is not provided along with the transformation to be updated, notification will be deleted.
    - Values specified as ``${VALUE}`` are treated as environment variables while ``VALUE`` is directly used as the actual value.
    - Old ``jetfire-cli`` style manifests can be used by adding ``legacy: true`` inside the old manifest.

.. literalinclude:: transformation_oidc.yaml
  :language: YAML

.. literalinclude:: transformation_apikey.yaml
  :language: YAML