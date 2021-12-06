import uuid
from typing import Dict, Optional

from click.testing import CliRunner
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation, TransformationDestination

from cognite.transformations_cli.commands.delete import delete

# TODO implement integration tests, parse configs -> upsert


def test_delete_by_id(exp_client: ExpCogniteClient, cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    uuid_conf = str(uuid.uuid1())
    created = exp_client.transformations.create(
        Transformation(
            external_id=uuid_conf,
            name=uuid_conf,
            query="select * from asd",
            destination=TransformationDestination.assets(),
            conflict_mode="upsert",
        )
    )
    assert exp_client.transformations.retrieve(created.id) is not None
    result = cli_runner.invoke(delete, [f"--id={created.id}"], obj=obj)
    assert result.exit_code == 0
    assert f"Successfully deleted the transformation with id {created.id}.\n" == result.output
    assert exp_client.transformations.retrieve(created.id) is None


def test_delete_by_external_id(
    exp_client: ExpCogniteClient, cli_runner: CliRunner, obj: Dict[str, Optional[str]]
) -> None:
    uuid_conf = str(uuid.uuid1())
    exp_client.transformations.create(
        Transformation(
            external_id=uuid_conf,
            name=uuid_conf,
            query="select * from asd",
            destination=TransformationDestination.assets(),
            conflict_mode="upsert",
        )
    )
    assert exp_client.transformations.retrieve(external_id=uuid_conf) is not None
    result = cli_runner.invoke(delete, [f"--external-id={uuid_conf}"], obj=obj)
    assert result.exit_code == 0
    assert f"Successfully deleted the transformation with external id {uuid_conf}.\n" == result.output
    assert exp_client.transformations.retrieve(external_id=uuid_conf) is None


def test_delete_by_both_ids(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(delete, ["--external-id=asd", "--id=1"], obj=obj)
    assert result.exit_code == 1
    assert result.exc_info[1].args[0] == "Please only provide one of id and external id."


def test_delete_by_no_ids(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(delete, obj=obj)
    assert result.exit_code == 1
    assert result.exc_info[1].args[0] == "Please provide one of id and external id."


def test_delete_by_invalid_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(delete, ["--id=10000000000000"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output


def test_delete_by_invalid_external_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(delete, ["--external-id=emelemelemelemel"], obj=obj)
    assert result.exit_code == 1
