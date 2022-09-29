import uuid
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from click.testing import CliRunner
from cognite.client import CogniteClient
from cognite.client.data_classes import (
    DataSet,
    Transformation,
    TransformationJobStatus,
    TransformationNotification,
    TransformationSchedule,
)
from cognite.client.data_classes.transformations.common import (
    DataModelInstances,
    SequenceRows,
    TransformationDestination,
)

from cognite.transformations_cli.commands.deploy.deploy import deploy
from cognite.transformations_cli.commands.deploy.transformations_api import (
    upsert_notifications,
    upsert_schedules,
    upsert_transformations,
)
from tests.test_config import rmdir, write_config


@pytest.mark.parametrize(
    "path, output, exit_code",
    [
        (
            "tests/invalid_example",
            "Failed to parse transformation config, please check that you conform required fields and format:",
            1,
        ),
        ("tests/oidc_examples", "Number of", 0),
        ("invalid_path", "Transformation root folder not found: invalid_path", 1),
    ],
)
def test_deploy(path: str, output: str, exit_code: int, cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    cli_result = cli_runner.invoke(deploy, [path], obj=obj)
    assert output in cli_result.output
    assert cli_result.exit_code == exit_code


def test_deploy_with_ds_and_run(
    cli_runner: CliRunner, obj: Dict[str, Optional[str]], new_dataset: DataSet, client: CogniteClient
) -> None:
    test_name = "test_deploy_with_ds_and_run"
    external_id = str(uuid.uuid1())
    file = f"""
        externalId: {external_id}
        name: {external_id}
        query: select 'test' as key, 'test' as name
        authentication:
            clientId: ${{CLIENT_ID}}
            clientSecret: ${{CLIENT_SECRET}}
            tokenUrl: "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"
            scopes:
                - "https://bluefield.cognitedata.com/.default"
            cdfProjectName: "extractor-bluefield-testing"
        destination:
            type: raw
            rawDatabase: testDb
            rawTable: testTable
        shared: true
        ignoreNullFields: False
        action: upsert
        dataSetId: {new_dataset.id}
        """
    write_config(test_name, file, 0)
    # test deploying the transformation with data set ID
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.external_id == external_id
    assert new_conf.query == "select 'test' as key, 'test' as name"
    # TODO: check for source and destination sessions when they are added to sdk
    # assert new_conf.has_source_oidc_credentials
    # assert new_conf.has_destination_oidc_credentials
    assert new_conf.destination.type == "raw"
    assert new_conf.data_set_id == new_dataset.id

    # test clearing the data set ID on the transformation
    file = file.replace(f"dataSetId: {new_dataset.id}", "dataSetId: null")
    file = file.replace(f"name: {external_id}", "name: testCLI")
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.data_set_id is None
    assert new_conf.name == "testCLI"

    # test updating the data set ID on the transformation
    file = file.replace("dataSetId: null", f"dataSetId: {new_dataset.id}")
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.data_set_id == new_dataset.id

    # test if it fails when data set ID and data set External ID are provided at the same time
    file = file + "dataSetExternalId: test"
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 1

    # test updating the data set ID on the transformation by the data set external ID
    file = file.replace("dataSetExternalId: test", "dataSetExternalId: cli-transformation-ds")
    file = file.replace(f"dataSetId: {new_dataset.id}", "")
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.data_set_id == new_dataset.id

    # test if it fails when an invalid data set external ID is provided
    file = file.replace("dataSetExternalId: cli-transformation-ds", "dataSetExternalId: non-existing")
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 1

    # run the deployed transformation to check the validity
    job = new_conf.run(wait=True)
    assert job.status == TransformationJobStatus.COMPLETED
    client.transformations.delete(external_id=external_id, ignore_unknown_ids=True)
    rmdir(Path(test_name))


def test_deploy_dmi_transformation(
    cli_runner: CliRunner, obj: Dict[str, Optional[str]], new_dataset: DataSet, client: CogniteClient
) -> None:
    test_name = "test_deploy_"
    external_id = str(uuid.uuid1())
    file = f"""
        externalId: {external_id}
        name: {external_id}
        query: select 'test' as key, 'test' as name
        authentication:
            clientId: ${{CLIENT_ID}}
            clientSecret: ${{CLIENT_SECRET}}
            tokenUrl: "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"
            scopes:
                - "https://bluefield.cognitedata.com/.default"
            cdfProjectName: "extractor-bluefield-testing"
        destination:
            type: data_model_instances
            model_external_id: test_model
            space_external_id: test_space
            instance_space_external_id: test_space
        shared: true
        ignoreNullFields: False
        action: upsert
        """
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.external_id == external_id
    my_dest: DataModelInstances = new_conf.destination
    assert my_dest.model_external_id == "test_model"
    client.transformations.delete(external_id=external_id, ignore_unknown_ids=True)
    rmdir(Path(test_name))


def test_deploy_sequence_rows_transformation(
    cli_runner: CliRunner, obj: Dict[str, Optional[str]], new_dataset: DataSet, client: CogniteClient
) -> None:
    test_name = "test_deploy_"
    external_id = str(uuid.uuid1())
    file = f"""
        externalId: {external_id}
        name: {external_id}
        query: select 'test' as key, 'test' as name
        authentication:
            clientId: ${{CLIENT_ID}}
            clientSecret: ${{CLIENT_SECRET}}
            tokenUrl: "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"
            scopes:
                - "https://bluefield.cognitedata.com/.default"
            cdfProjectName: "extractor-bluefield-testing"
        destination:
            type: sequence_rows
            externalId: test_sequence
        shared: true
        ignoreNullFields: False
        action: upsert
        """
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.external_id == external_id
    assert new_conf.destination == SequenceRows("test_sequence")
    client.transformations.delete(external_id=external_id, ignore_unknown_ids=True)
    rmdir(Path(test_name))


def test_deploy_transformation_with_tags(
    cli_runner: CliRunner, obj: Dict[str, Optional[str]], new_dataset: DataSet, client: CogniteClient
) -> None:
    test_name = "test_deploy_"
    external_id = str(uuid.uuid1())
    import time

    tag_postfix = time.time()
    tag1 = f"emel_{tag_postfix}"
    tag2 = f"OPs_{tag_postfix}"
    tag3 = f"bye_{tag_postfix}"

    base_manifest = f"""
        externalId: {external_id}
        name: {external_id}
        query: select 'test' as key, 'test' as name
        authentication:
            clientId: ${{CLIENT_ID}}
            clientSecret: ${{CLIENT_SECRET}}
            tokenUrl: "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"
            scopes:
                - "https://bluefield.cognitedata.com/.default"
            cdfProjectName: "extractor-bluefield-testing"
        destination: assets
        shared: true
        ignoreNullFields: False
        action: upsert
    """
    # This manifest should create a new transformation with tags
    file = f"""
        {base_manifest}
        tags:
            - {tag1}
            - {tag2}
        """
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert set(new_conf.tags) == set([tag1, tag2])

    # This manifest should overwrite tags with new values
    file = f"""
        {base_manifest}
        tags:
            - {tag3}
        """
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.tags == [tag3]

    # This manifest should clear tags as they are not provided.
    write_config(test_name, base_manifest, 0)
    cli_result = cli_runner.invoke(deploy, [test_name], obj=obj)
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert cli_result.exit_code == 0
    assert new_conf.external_id == external_id
    assert new_conf.tags is None

    client.transformations.delete(external_id=external_id, ignore_unknown_ids=True)
    rmdir(Path(test_name))


def test_deploy_old_config_with_legacy_flag(
    cli_runner: CliRunner, obj: Dict[str, Optional[str]], new_dataset: DataSet, client: CogniteClient
) -> None:
    test_name = "test_deploy_"
    query_file_name = "sqlFile"
    external_id = str(uuid.uuid1())
    write_config(query_file_name, "select 'asd' as name, 'asd' as externalId", 0, "sql")
    file = f"""
        externalId: {external_id}
        name: {external_id}
        query: ../{query_file_name}/trans_0.sql
        authentication:
            read:
                clientId: CLIENT_ID
                clientSecret: CLIENT_SECRET
                tokenUrl: "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"
                scopes:
                    - "https://bluefield.cognitedata.com/.default"
                cdfProjectName: "extractor-bluefield-testing"
            write:
                clientId: CLIENT_ID
                clientSecret: CLIENT_SECRET
                tokenUrl: "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"
                scopes:
                    - "https://bluefield.cognitedata.com/.default"
                cdfProjectName: "extractor-bluefield-testing"
        schedule: "* * * * *"
        destination: "assets"
        notifications:
            - notif1
            - notif2
        shared: true
        ignoreNullFields: False
        action: upsert
        """
    write_config(test_name, file, 0)
    cli_result = cli_runner.invoke(deploy, [test_name, "--legacy-mode"], obj=obj)
    assert cli_result.exit_code == 0
    new_conf = client.transformations.retrieve(external_id=external_id)
    assert new_conf.external_id == external_id
    assert new_conf.destination == TransformationDestination.assets()
    # run the deployed transformation to check the validity
    job = new_conf.run(wait=True)
    assert job.status == TransformationJobStatus.COMPLETED
    client.transformations.delete(external_id=external_id, ignore_unknown_ids=True)
    rmdir(Path(test_name))
    rmdir(Path(query_file_name))


def test_upsert_transformations(
    client: CogniteClient,
    test_transformation_ext_ids: List[str],
    configs_to_create: List[Transformation],
) -> None:
    # Scenario 1:
    # All the transformations are new, all should be created
    _, updated, created = upsert_transformations(client, configs_to_create[:3], [], test_transformation_ext_ids[:3])
    assert len(updated) == 0
    assert len(created) == 3

    # Scenario 2:
    # tr1, tr3 exists and transformations should be updated
    # tr4 is a new transformation, it will be created
    configs_to_update = [
        Transformation(
            external_id=test_transformation_ext_ids[0],
            ignore_null_fields=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[2],
            name="updated-name-conf3",
            conflict_mode="upsert",
            query="select 'asd2' as externalId",
        ),
    ]

    _, updated, created = upsert_transformations(
        client,
        configs_to_update + [configs_to_create[3]],
        [i.external_id for i in configs_to_update],
        [test_transformation_ext_ids[3]],
    )
    assert len(updated) == 2
    assert len(created) == 1
    # Clean up after the test
    client.transformations.schedules.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
    client.transformations.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)


def test_upsert_notifications(
    client: CogniteClient, test_transformation_ext_ids: List[str], configs_to_create: List[Transformation]
) -> None:
    # Create transformations
    tr1, tr2, tr3, _ = test_transformation_ext_ids
    client.transformations.create(configs_to_create)
    # Prepare test data
    existing_notifications = client.transformations.notifications.create(
        [
            TransformationNotification(transformation_external_id=tr1, destination="a@transformations-cli.com"),
            TransformationNotification(transformation_external_id=tr1, destination="b@transformations-cli.com"),
        ]
    )  # create existing notifications
    requested_notifications = {
        tr1: [TransformationNotification(transformation_external_id=tr1, destination="a@transformations-cli.com")],
        tr2: [TransformationNotification(transformation_external_id=tr2, destination="d@transformations-cli.com")],
        tr3: [TransformationNotification(transformation_external_id=tr3, destination="c@transformations-cli.com")],
    }

    # Scenario: Assumed that tr1 and tr2 are existing transformations, tr3 is newly created by deploy command.
    # Now, it is time to create notifications after upserting transformations.
    # tr1 will have one deleted and one of the requested notifications already exists, no effect. tr2 and tr3 will have 2 created in total.
    deleted, _, created = upsert_notifications(
        client=client,
        existing_notifications_dict={tr1: existing_notifications},
        requested_notifications_dict=requested_notifications,
        existing_transformations_ext_ids=[tr1, tr2],
        new_transformations_ext_ids=[tr3],
    )
    assert len(deleted) == 1
    assert len(created) == 2
    # Clean up after the test
    client.transformations.schedules.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
    client.transformations.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)


def test_upsert_schedules(
    client: CogniteClient, test_transformation_ext_ids: List[str], configs_to_create: List[Transformation]
) -> None:
    tr1_ext_id, tr2_ext_id, tr3_ext_id, tr4_ext_id = test_transformation_ext_ids
    # Create transformations
    client.transformations.create(configs_to_create)
    # Create schedules to test delete and update
    existing_schedules = [
        TransformationSchedule(external_id=tr1_ext_id, interval="5 4 * * *", is_paused=False),
        TransformationSchedule(external_id=tr2_ext_id, interval="5 4 * * *", is_paused=False),
    ]
    client.transformations.schedules.create(existing_schedules)

    # Scenario: Assumed that tr1, tr2, tr3 are existing transformations, tr4 is newly created by deploy command.
    # Now, it is time to create notifications after upserting transformations.
    # tr1 is scheduled but later on schedule upsert will see it should be unscheduled.
    # tr2 is scheduled and has a new schedule in deployment, update will happen.
    # tr3 has a new schedule to create.
    # tr4 is a new transformations created by this deploy scenario, as it is a new transformation, schedule will be created.
    requested_schedules = {
        tr2_ext_id: TransformationSchedule(external_id=tr2_ext_id, interval="5 2 * * *", is_paused=False),  # update
        tr3_ext_id: TransformationSchedule(
            external_id=tr3_ext_id, interval="5 3 * * *", is_paused=False
        ),  # new but existing transformation
        tr4_ext_id: TransformationSchedule(external_id=tr4_ext_id, interval="5 5 * * *", is_paused=False),
    }  # treat tr4 as a new transformation to see if schedule created for a new transformation
    existing_schedules_dict = {s.external_id: s for s in existing_schedules}
    deleted, updated, created = upsert_schedules(
        client, existing_schedules_dict, requested_schedules, [tr1_ext_id, tr2_ext_id, tr3_ext_id], [tr4_ext_id]
    )
    assert len(deleted) == 1
    assert len(updated) == 1
    assert len(created) == 2
    # Clean up after the test
    client.transformations.schedules.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
    client.transformations.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
