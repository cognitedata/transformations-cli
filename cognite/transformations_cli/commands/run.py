import sys
import time
from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_client
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
    "--external-id", help="The external_id of the transformation to run. Either this or --id must be specified."
)
@click.option("--watch", is_flag=True, help="Wait until job has completed.")
@click.option(
    "--watch-only",
    is_flag=True,
    help="Do not start a transformation job, only watch the most recent job for completion.",
)
@click.option(
    "--time-out",
    default=(12 * 60 * 60),
    help="Maximum amount of time to wait for job to complete in seconds, 12 hours by default.",
)
@click.pass_obj
def run(
    obj: Dict,
    id: Optional[int],
    external_id: Optional[str],
    watch: bool = False,
    watch_only: bool = False,
    time_out: int = (12 * 60 * 60),
) -> None:
    client = get_client(obj)
    is_id_provided(id, external_id)
    is_id_exclusive(id, external_id)
    try:
        job = None
        # TODO Investigate why id requires type casting as it doesn't in "jobs command"
        id = int(id) if id else None
        if not watch_only:
            duration_start = time.time()
            job = client.transformations.run(
                transformation_id=id, transformation_external_id=external_id, wait=watch, timeout=time_out
            )
            duration_end = time.time()
        else:
            jobs = client.transformations.jobs.list(transformation_id=id, transformation_external_id=external_id)

            duration_start = time.time()
            job = jobs[0].wait(timeout=time_out) if jobs else None
            duration_end = time.time()
        if job:
            metrics = [
                m
                for m in client.transformations.jobs.list_metrics(id=job.id)
                if m.name != "requestsWithoutRetries" and m.name != "requests"
            ]
            click.echo("Job details:")
            click.echo(print_jobs([job]))
            click.echo("SQL Query:")
            click.echo(print_sql(job.query))
            if job.status == "Failed":
                click.echo(f"Job Failed, error details: {job.error}")
            if metrics:
                click.echo("Progress:")
                click.echo(print_metrics(metrics))
            if watch_only or watch:
                if job.status == "Failed":
                    # Error already been printed so just exit.
                    sys.exit(1)
                if duration_end - duration_start > (time_out + 1) and job.status != "Completed":
                    click.echo(f"Transformation job runtime exceeds the provided timeout: {time_out} seconds")
                    sys.exit(1)
    # Handle AttributeError because SDK fails here:
    # transformation_id = self.retrieve(external_id=transformation_external_id).id
    # with "AttributeError: 'NoneType' object has no attribute 'id'"
    # when called with invalid external_id
    # We mask that here with this trick until solved.
    except AttributeError:
        click.echo("Cognite API error has occurred: Transformation not found.")
        sys.exit(1)
    except (CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
