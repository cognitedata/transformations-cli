from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import exit_with_cognite_api_error, is_id_exclusive, is_id_provided


@click.command(help="Delete a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.pass_obj
def delete(obj: Dict, id: Optional[int], external_id: Optional[str]) -> None:
    _, exp_client = get_clients(obj)
    id = int(id) if id else None
    is_id_provided(id, external_id)
    is_id_exclusive(id, external_id)
    try:
        exp_client.transformations.delete(external_id=external_id, id=id)
        if id:
            click.echo(f"Successfully deleted the transformation with id {id}.")
        else:
            click.echo(f"Successfully deleted the transformation with external id {external_id}.")
    except (CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
