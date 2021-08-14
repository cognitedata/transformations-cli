from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients


@click.command(help="Delete a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.pass_obj
def delete(obj: Dict, id: Optional[int], external_id: Optional[str]) -> None:
    _, exp_client = get_clients(obj)
    if not id and not external_id:
        exit("Please provide a valid transformation id or external_id")
    try:
        if id:
            click.echo(f"Deleting the transformation with id {id}...")
            exp_client.transformations.delete(id=id)
        else:
            click.echo(f"Deleting the transformation with external id {external_id}...")
            exp_client.transformations.delete(external_id=external_id)
        click.echo("Successfully deleted.")
    except CogniteNotFoundError as e:
        exit(f"Id not found: {e}")
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
