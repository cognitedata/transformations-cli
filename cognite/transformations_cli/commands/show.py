from typing import Dict, Optional, Tuple

import click
from cognite.client.exceptions import CogniteAPIError
from cognite.experimental.data_classes.transformation_jobs import TransformationJob
from cognite.experimental.data_classes.transformations import Transformation

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    is_id_exclusive,
    print_jobs,
    print_metrics,
    print_notifications,
    print_sql,
    print_transformations,
)


@click.command(help="Show detalis of a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.option(
    "--job-id", help="The id of the job to show. Include this to show job details instead of transformation details."
)
@click.pass_obj
def show(
    obj: Dict, id: Optional[int], external_id: Optional[str], job_id: Optional[int]
) -> Tuple[Optional[Transformation], Optional[TransformationJob]]:
    _, exp_client = get_clients(obj)
    is_id_exclusive(id, external_id)
    try:
        tr = None
        job = None
        if id or external_id:
            # TODO Investigate why id requires type casting as it doesn't in "jobs command"
            id = int(id) if id else None
            tr = exp_client.transformations.retrieve(id=int(id) if id else None, external_id=external_id)
            click.echo("Transformation details:")
            click.echo(print_transformations([tr]))
            notifications = exp_client.transformations.notifications.list(
                transformation_id=id, transformation_external_id=external_id
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
            job = exp_client.transformations.jobs.retrieve(id=int(job_id))
            metrics = [
                m
                for m in exp_client.transformations.jobs.list_metrics(id=job_id)
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
        return tr, job
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
        return None, None
