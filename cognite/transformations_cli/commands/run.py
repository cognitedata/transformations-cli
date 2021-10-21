from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    is_id_exclusive,
    is_id_provided,
    print_jobs,
    print_metrics,
    print_sql,
)


@click.command(help="Start and/or watch transformation jobs")
@click.option("--id", help="The id of the transformation to run. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to run. Either this or --id must be specified."
)
@click.option("--watch", is_flag=True, help="Wait until job has completed")
@click.option(
    "--watch-only",
    is_flag=True,
    help="Do not start a transformation job, only watch the most recent job for completion",
)
@click.option(
    "--time-out", default=(12 * 60 * 60), help="Maximum amount of time to wait for job to complete in seconds"
)
@click.pass_obj
def run(
    obj: Dict,
    id: Optional[int],
    external_id: Optional[str],
    watch: bool = False,
    watch_only: bool = False,
    time_out: Optional[int] = None,
) -> None:
    _, exp_client = get_clients(obj)
    is_id_provided(id, external_id)
    is_id_exclusive(id, external_id)
    try:
        job = None
        # TODO Investigate why id requires type casting as it doesn't in "jobs command"
        id = int(id) if id else None
        if not watch_only:
            job = exp_client.transformations.run(
                transformation_id=id, transformation_external_id=external_id, wait=watch, timeout=time_out
            )
        else:
            if external_id:
                id = exp_client.transformations.retrieve(external_id=external_id).id
            jobs = exp_client.transformations.jobs.list(transformation_id=id)
            job = jobs[0].wait(timeout=time_out) if jobs else None
        if job:
            metrics = [
                m
                for m in exp_client.transformations.jobs.list_metrics(id=job.id)
                if m.name != "requestsWithoutRetries" and m.name != "requests"
            ]
            click.echo("Job details:")
            click.echo(print_jobs([job]))
            click.echo("SQL Query:")
            click.echo(print_sql(job.raw_query))
            if job.status == "Failed":
                click.echo(f"Error Details: {job.error}")
            if metrics:
                click.echo("Progress:")
                click.echo(print_metrics(metrics))
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
