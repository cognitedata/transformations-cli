from typing import Dict, List, Optional

from click.testing import CliRunner
from cognite.client import CogniteClient
from cognite.client.data_classes import Transformation, TransformationNotification

from cognite.transformations_cli.commands.show import show
from tests.helpers import from_table


def test_show_with_id(
    client: CogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = client.transformations.create(configs_to_create[0])
    tr_id = tr.id
    notif = client.transformations.notifications.create(
        TransformationNotification(transformation_id=tr_id, destination="emel")
    )
    cli_result = cli_runner.invoke(show, [f"--id={tr_id}"], obj=obj)
    client.transformations.delete(id=tr_id)

    assert cli_result.exit_code == 0

    cli_result_list = from_table(cli_result.output)
    assert str(tr_id) in cli_result_list[2]
    assert tr.external_id in cli_result_list[2]
    assert "SELECT 'asd' AS name," == " ".join(cli_result_list[4])
    assert "'asd' AS externalId" == " ".join(cli_result_list[5])
    assert str(notif.id) in cli_result_list[8]
    assert str(tr_id) in cli_result_list[8]
    assert notif.destination in cli_result_list[8]


def test_show_with_external_id(
    client: CogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    external_id = configs_to_create[0].external_id
    tr = client.transformations.create(configs_to_create[0])
    notif = client.transformations.notifications.create(
        TransformationNotification(transformation_external_id=external_id, destination="emel")
    )

    cli_result = cli_runner.invoke(show, [f"--external-id={external_id}"], obj=obj)
    client.transformations.delete(external_id=external_id)

    assert cli_result.exit_code == 0

    cli_result_list = from_table(cli_result.output)
    assert str(tr.id) in cli_result_list[2]
    assert tr.external_id in cli_result_list[2]
    assert "SELECT 'asd' AS name," == " ".join(cli_result_list[4])
    assert "'asd' AS externalId" == " ".join(cli_result_list[5])
    assert str(notif.id) in cli_result_list[8]
    assert str(tr.id) in cli_result_list[8]
    assert notif.destination in cli_result_list[8]


def test_show_with_job_id(
    client: CogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = client.transformations.create(configs_to_create[0])
    job = tr.run(wait=True)
    job_id = job.id
    cli_result = cli_runner.invoke(show, [f"--job-id={job_id}"], obj=obj)
    client.transformations.delete(id=tr.id)
    # TODO more detailed testing of the output
    assert cli_result.exit_code == 0


def test_show_both_ids(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    cli_result = cli_runner.invoke(show, ["--external-id=asd, --id=1"], obj=obj)
    assert cli_result.exit_code == 1


def test_show_by_invalid_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(show, ["--id=10000000000000"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output


def test_show_by_invalid_external_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(show, ["--external-id=emelemelemelemel"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output


def test_show_by_invalid_job_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(show, ["--job-id=10000000000000"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output
