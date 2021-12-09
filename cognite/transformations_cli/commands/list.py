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
@click.option(
    "-i", "--interactive", is_flag=True, help="Display only 10 transformations at a time, then page through them."
)
@click.pass_obj
def list(obj: Dict, limit: int = 10, interactive: bool = False) -> None:
    client = get_client(obj)
    try:
        transformations = client.transformations.list(limit=limit)
        if interactive:
            paginate(transformations, log_transformations)
        else:
            log_transformations(transformations)
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
