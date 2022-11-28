import sys
from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_client
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    get_transformation,
    is_id_exclusive,
    print_jobs,
    print_metrics,
    print_notifications,
    print_sql,
    print_transformations,
)


@click.command(help="Show details of a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id can be specified.")
@click.option(
    "--external-id", help="The external_id of the transformation to show. Either this or --id can be specified."
)
@click.option("--job-id", help="The id of the job to show. Include this to show job details.")
@click.pass_obj
def show(obj: Dict, id: Optional[int], external_id: Optional[str], job_id: Optional[int]) -> None:
    client = get_client(obj)
    is_id_exclusive(id, external_id)
    if not (id or external_id or job_id):
        click.echo("Please provide id, external_id or job_id")
        sys.exit(1)
    try:
        tr = None
        job = None
        if id or external_id:
            # TODO Investigate why id requires type casting as it doesn't in "jobs command"
            id = int(id) if id else None
            tr = get_transformation(client=client, id=id, external_id=external_id)
            click.echo("Transformation details:")
            click.echo(print_transformations([tr]))
            notifications = client.transformations.notifications.list(
                transformation_id=id, transformation_external_id=external_id, limit=-1
            )
            if tr.query:
                click.echo("SQL Query:")
                click.echo(print_sql(tr.query))
            if notifications:
                click.echo("Notifications:")
                click.echo(print_notifications(notifications))
        if job_id:
            click.echo()
            job_id = int(job_id)
            job = client.transformations.jobs.retrieve(id=int(job_id))
            metrics = [
                m
                for m in client.transformations.jobs.list_metrics(id=job_id)
                if m.name != "requestsWithoutRetries" and m.name != "requests"
            ]
            click.echo("Job details:")
            click.echo(print_jobs([job]))
            click.echo("SQL Query:")
            click.echo(print_sql(job.query))
            if job.status == "Failed":
                click.echo(f"Error Details: {job.error}")
            if metrics:
                click.echo("Progress:")
                click.echo(print_metrics(metrics))
    except (CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
