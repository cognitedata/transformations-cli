from typing import Dict, List, Optional

from click.testing import CliRunner
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation

from cognite.transformations_cli.commands.run import run
from tests.helpers import from_table


def test_run_with_id(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[1])
    tr_id = tr.id
    cli_result = cli_runner.invoke(run, [f"--id={tr_id}", "--watch"], obj=obj)
    exp_client.transformations.delete(id=tr_id)

    assert cli_result.exit_code == 0

    cli_result_list = from_table(cli_result.output)
    assert "Completed" in cli_result_list[2] or "Failed" in cli_result_list[2]
    assert str(tr_id) in cli_result_list[2]
    assert "SELECT 'asd' AS KEY," == " ".join(cli_result_list[4])
    assert "'asd' AS externalId" == " ".join(cli_result_list[5])


def test_run_with_external_id(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[2])
    external_id = tr.external_id
    cli_result = cli_runner.invoke(run, [f"--external-id={external_id}"], obj=obj)
    exp_client.transformations.delete(external_id=external_id)

    assert cli_result.exit_code == 0

    cli_result_list = from_table(cli_result.output)
    assert (
        "Created" in cli_result_list[2]
        or "Running" in cli_result_list[2]
        or "Completed" in cli_result_list[2]
        or "Failed" in cli_result_list[2]
    )
    assert "SELECT 'asd' AS externalId" == " ".join(cli_result_list[4])


def test_watch_only(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[3])
    tr.run(wait=True)
    external_id = tr.external_id
    cli_result = cli_runner.invoke(run, [f"--external-id={external_id}", "--watch-only"], obj=obj)

    jobs = exp_client.transformations.jobs.list(transformation_id=tr.id)
    assert len(jobs) == 1  # check that 'run' didn't generate a new job as it is watch-only mode
    exp_client.transformations.delete(external_id=external_id)

    assert cli_result.exit_code == 1

    cli_result_list = from_table(cli_result.output)
    assert "Failed" in cli_result_list[2]
    assert "SELECT 'asd' AS externalId 'asd' AS name" == " ".join(cli_result_list[4])
    assert "mismatched input ''asd'' expecting {<EOF>, ';'}(line 1, pos 27)" == " ".join(cli_result_list[6])


def test_run_by_invalid_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(run, ["--id=10000000000000"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output


def test_run_by_invalid_external_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(run, ["--external-id=emelemelemelemel"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output
