from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError

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
    "--job", help="The id of the job to show. Include this to show job details instead of transformation details."
)
@click.pass_obj
def show(obj: Dict, id: Optional[int], external_id: Optional[str], job: Optional[int]) -> None:
    _, exp_client = get_clients(obj)
    is_id_exclusive(id, external_id)
    try:
        if id or external_id:
            # TODO Investigate why id requires type casting as it doesn't in "jobs command"
            id = int(id) if id else None
            tr = exp_client.transformations.retrieve(id=int(id) if id else None, external_id=external_id)
            click.echo("\nTransformation details:\n")
            click.echo(print_transformations([tr]))
            notifications = exp_client.transformations.notifications.list(
                transformation_id=id, transformation_external_id=external_id
            )
            if tr.query:
                click.echo("\nSQL Query:\n")
                click.echo(print_sql(tr.query))
            if notifications:
                click.echo("\nNotifications:\n")
                click.echo(print_notifications(notifications))
        if job:
            job = int(job)
            j = exp_client.transformations.jobs.retrieve(id=int(job))
            click.echo("\nJob details:\n")
            click.echo(print_jobs([j]))
            click.echo("\nSQL Query:\n")
            click.echo(print_sql(j.raw_query))
            if j.status == "Failed":
                click.echo(f"\nError Details: {j.error}\n")
            metrics = filter(
                lambda m: m.name != "requestsWithoutRetries" and m.name != "requests",
                exp_client.transformations.jobs.list_metrics(id=job),
            )
            if list(metrics):
                click.echo("Progress:\n")
                click.echo(print_metrics(metrics))
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
