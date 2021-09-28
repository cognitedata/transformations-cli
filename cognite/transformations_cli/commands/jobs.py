from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients


@click.command(help="Show latest jobs for a given transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.option("--limit", default=10, help="Limit for the job history, defaults to 10. Use -1 to retrieve all results.")
@click.pass_obj
# TODO format before printing
def jobs(obj: Dict, id: Optional[int], external_id: Optional[str], limit: int = 10) -> None:
    _, exp_client = get_clients(obj)
    intro_str = (
        f" for transformation with id {id}..."
        if id
        else f" for transformation with external_id {external_id}..."
        if external_id
        else "..."
    )
    click.echo(f"Listing latest jobs{intro_str}")
    if id and external_id:
        exit("Please only provide one of id and external id.")
    try:
        if external_id:
            id = exp_client.transformations.retrieve(external_id=external_id).id
        if id:
            jobs = exp_client.transformations.jobs.list(limit=-1)
            limit = limit if limit != -1 else len(jobs)
            jobs = [job for job in jobs if job.transformation_id == id][:limit]
        else:
            jobs = exp_client.transformations.jobs.list(limit=limit)

        click.echo("Resulting jobs:")
        click.echo(jobs)
    except CogniteNotFoundError as e:
        exit(f"Id not found: {e}")
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
