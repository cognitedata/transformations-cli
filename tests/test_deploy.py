from typing import Dict, List, Optional

import pytest
from click.testing import CliRunner
from cognite.client import CogniteClient
from cognite.client.data_classes import Transformation, TransformationNotification, TransformationSchedule

from cognite.transformations_cli.commands.deploy.deploy import deploy
from cognite.transformations_cli.commands.deploy.transformations_api import (
    upsert_notifications,
    upsert_schedules,
    upsert_transformations,
)


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
