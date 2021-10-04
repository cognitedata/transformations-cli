from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    exit_with_id_not_found,
    is_id_exclusive,
)


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
    is_id_exclusive(id, external_id)
    try:
        if id:
            click.echo(f"Listing the latest jobs for transformation with id {id}")
        if external_id:
            id = exp_client.transformations.retrieve(external_id=external_id).id
            click.echo(f"Listing the latest jobs for transformation with external_id {external_id}")
        jobs = exp_client.transformations.jobs.list(limit=limit, transformation_id=id)
        click.echo("Resulting jobs:")
        click.echo(jobs)
    except CogniteNotFoundError as e:
        exit_with_id_not_found(e)
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
