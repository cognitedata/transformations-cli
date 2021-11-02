from typing import Dict, List, Optional

from click.testing import CliRunner
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation

from cognite.transformations_cli.commands.jobs import jobs
from cognite.transformations_cli.commands.utils import print_jobs


def test_jobs(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])
    tr.run(wait=False)  # Make sure we have at least 1 job in the tenant
    result = cli_runner.invoke(jobs, ["--limit=1"], obj=obj)
    exp_client.transformations.delete(id=tr.id, ignore_unknown_ids=True)
    assert result.exit_code == 0
    assert len(result.output.strip().split("\n")) == 6  # Table with 1 result takes 6 lines


def test_jobs_by_id(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])
    result_job = tr.run(wait=True)  # Make sure transformation has a job and it is finished so we can check the output.
    result = cli_runner.invoke(jobs, [f"--id={tr.id}"], obj=obj)
    exp_client.transformations.delete(id=tr.id, ignore_unknown_ids=True)
    assert result.exit_code == 0
    assert result.output.replace("\n", "").replace(" ", "") == (
        f"Listing the latest jobs for transformation with id {tr.id}:Resulting jobs:" + print_jobs([result_job])
    ).replace("\n", "").replace(" ", "")


def test_jobs_by_external_id(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
    configs_to_create: List[Transformation],
) -> None:
    tr = exp_client.transformations.create(configs_to_create[0])
    result_job = tr.run(wait=True)  # Make sure transformation has a job and it is finished so we can check the output.
    result = cli_runner.invoke(jobs, [f"--external-id={tr.external_id}"], obj=obj)
    exp_client.transformations.delete(id=tr.id, ignore_unknown_ids=True)
    assert result.exit_code == 0
    assert result.output.replace("\n", "").replace(" ", "") == (
        f"Listing the latest jobs for transformation with external_id {tr.external_id}:Resulting jobs:"
        + print_jobs([result_job])
    ).replace("\n", "").replace(" ", "")
