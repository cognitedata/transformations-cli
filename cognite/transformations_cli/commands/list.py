from typing import Dict

import click
from cognite.client.exceptions import CogniteAPIError

from cognite.transformations_cli.clients import get_clients


@click.command(help="List transformations")
@click.option("--limit", default=10, help="Number of transformations to list, defaults to 10. Use -1 to list all.")
@click.pass_obj
# TODO idea: make this interactive, user can go back and forth through pages
# format before printing
def list(obj: Dict, limit: int = 10) -> None:
    _, exp_client = get_clients(obj)
    try:
        click.echo(exp_client.transformations.list(limit=limit))
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
