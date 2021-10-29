import uuid

import pytest
from click.testing import CliRunner
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation, TransformationDestination

from cognite.transformations_cli.commands.base import transformations_cli


@pytest.mark.unit
def test_delete_by_id(exp_client: ExpCogniteClient) -> None:
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
    runner = CliRunner()
    result = runner.invoke(transformations_cli, ["delete", f"--id={created.id}"])
    assert result.exit_code == 0
    assert f"Successfully deleted the transformation with id {created.id}.\n" == result.output
    assert exp_client.transformations.retrieve(created.id) is None


@pytest.mark.unit
def test_delete_by_external_id(exp_client: ExpCogniteClient) -> None:
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
    runner = CliRunner()
    result = runner.invoke(transformations_cli, ["delete", f"--external-id={uuid_conf}"])
    assert result.exit_code == 0
    assert f"Successfully deleted the transformation with external id {uuid_conf}.\n" == result.output
    assert exp_client.transformations.retrieve(external_id=uuid_conf) is None


@pytest.mark.unit
def test_delete_by_both_ids() -> None:
    runner = CliRunner()
    result = runner.invoke(transformations_cli, ["delete", "--external-id=asd", "--id=1"])
    assert result.exit_code == 1
    assert result.exc_info[1].args[0] == "Please only provide one of id and external id."


@pytest.mark.unit
def test_delete_by_no_ids() -> None:
    runner = CliRunner()
    result = runner.invoke(transformations_cli, ["delete"])
    assert result.exit_code == 1
    assert result.exc_info[1].args[0] == "Please provide one of id and external id."
