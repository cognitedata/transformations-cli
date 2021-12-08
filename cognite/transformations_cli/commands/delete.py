from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_client
from cognite.transformations_cli.commands.utils import exit_with_cognite_api_error, is_id_exclusive, is_id_provided


@click.command(help="Delete a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The external_id of the transformation to show. Either this or --id must be specified."
)
@click.option("--delete-schedule", is_flag=False, help="Delete the schedule before deleting the transformation.")
@click.pass_obj
def delete(obj: Dict, id: Optional[int], external_id: Optional[str], delete_schedule: bool = False) -> None:
    client = get_client(obj)
    id = int(id) if id else None
    is_id_provided(id, external_id)
    is_id_exclusive(id, external_id)
    try:
        if delete_schedule:
            client.transformations.schedules.delete(external_id=external_id, id=id, ignore_unknown_ids=True)
        client.transformations.delete(external_id=external_id, id=id)
        if id:
            click.echo(f"Successfully deleted the transformation with id {id}.")
        else:
            click.echo(f"Successfully deleted the transformation with external id {external_id}.")
    except (CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
