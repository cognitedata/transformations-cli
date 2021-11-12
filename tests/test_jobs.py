from typing import Dict, List, Optional

from click.testing import CliRunner
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation

from cognite.transformations_cli.commands.jobs import jobs
from tests.helpers import from_table


def test_jobs(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])
    tr.run(wait=True)  # Make sure we have at least 1 job in the tenant

    cli_result = cli_runner.invoke(jobs, ["--limit=1"], obj=obj)

    exp_client.transformations.delete(id=tr.id, ignore_unknown_ids=True)  # Clean up

    cli_res_list = from_table(cli_result.output)
    assert len(cli_res_list) == 3  # Only 1 job produced, 2 lines for headers
    assert (
        "Running" in cli_res_list[2]
        or "Created" in cli_res_list[2]
        or "Completed" in cli_res_list[2]
        or "Failed" in cli_res_list[2]
    )  # Status is in the result
    assert cli_result.exit_code == 0


def test_jobs_by_id(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])
    result_job = tr.run(wait=True)  # Make sure transformation has a job and it is finished so we can check the output.

    cli_result = cli_runner.invoke(jobs, [f"--id={tr.id}"], obj=obj)

    exp_client.transformations.delete(id=tr.id, ignore_unknown_ids=True)  # Clean up

    cli_res_list = from_table(cli_result.output)
    assert str(tr.id) in cli_res_list[3]  # Transformation id is in the result
    assert str(result_job.id) in cli_res_list[3]  # Job id is in the result
    assert len(cli_res_list) == 4  # Only 1 job produced, 3 lines for headers
    assert "Completed" in cli_res_list[3] or "Failed" in cli_res_list[3]  # Status is in the result
    assert cli_result.exit_code == 0


def test_jobs_by_external_id(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])
    result_job = tr.run(wait=True)  # Make sure transformation has a job and it is finished so we can check the output.

    cli_result = cli_runner.invoke(jobs, [f"--external-id={tr.external_id}"], obj=obj)

    exp_client.transformations.delete(external_id=tr.external_id, ignore_unknown_ids=True)  # Clean up

    cli_res_list = from_table(cli_result.output)
    assert str(result_job.id) in cli_res_list[3]  # Job id is in the result
    assert len(cli_res_list) == 4  # Only 1 job produced, 3 lines for headers
    assert "Completed" in cli_res_list[3] or "Failed" in cli_res_list[3]  # Status is in the result
    assert cli_result.exit_code == 0


def test_jobs_by_invalid_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(jobs, ["--id=10000000000000"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output


def test_jobs_by_invalid_external_id(cli_runner: CliRunner, obj: Dict[str, Optional[str]]) -> None:
    result = cli_runner.invoke(jobs, ["--external-id=emelemelemelemel"], obj=obj)
    assert result.exit_code == 1
    assert "Cognite API error has occurred" in result.output


def test_jobs_by_id_with_no_jobs(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])  # Transformation with no jobs
    cli_result = cli_runner.invoke(jobs, [f"--id={tr.id}"], obj=obj)

    exp_client.transformations.delete(id=tr.id, ignore_unknown_ids=True)  # Clean up

    assert cli_result.exit_code == 0
    assert cli_result.output == f"Listing the latest jobs for transformation with id {tr.id}:\nNo jobs to list.\n"
