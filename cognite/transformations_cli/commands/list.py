from typing import Dict, List

import click
from cognite.client.data_classes import Transformation
from cognite.client.exceptions import CogniteAPIError

from cognite.transformations_cli.clients import get_client
from cognite.transformations_cli.commands.utils import paginate, print_transformations


def log_transformations(transformations: List[Transformation]) -> None:
    click.echo(print_transformations(transformations))


@click.command(help="List transformations")
@click.option("--limit", default=10, help="Number of transformations to list, defaults to 10. Use -1 to list all.")
@click.option("--data-set-id", "-d", multiple=True, help="Filter transformations by data set ID.")
@click.option("--data-set-external-id", "-e", multiple=True, help="Filter transformations by data set external ID.")
@click.option("--destination-type", help="Filter transformations by destination type")
@click.option("--conflict-mode", help="Filter transformations by conflict mode")
@click.option(
    "-i", "--interactive", is_flag=True, help="Display only 10 transformations at a time, then page through them."
)
@click.pass_obj
def list(
    obj: Dict,
    limit: int = 10,
    data_set_id: List[int] = None,
    data_set_external_id: List[int] = None,
    destination_type: str = None,
    conflict_mode: str = None,
    interactive: bool = False,
) -> None:
    client = get_client(obj)
    destination_type_new = (
        "data_model_instances" if destination_type == "alpha_data_model_instances" else destination_type
    )
    # Backend expects destination types in filter without "_", but destination types have "_" in them in other places
    # Manipulate it until it is fixed in the backend.
    destination_type_new = destination_type_new.replace("_", "") if destination_type_new else destination_type_new
    try:
        transformations = client.transformations.list(
            limit=limit,
            data_set_ids=data_set_id,
            data_set_external_ids=data_set_external_id,
            destination_type=destination_type_new,
            conflict_mode=conflict_mode,
        )
        if interactive:
            paginate(transformations, log_transformations)
        else:
            log_transformations(transformations)
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
