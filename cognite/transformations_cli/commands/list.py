from typing import Dict

import click
from cognite.client.exceptions import CogniteAPIError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import print_transformations


@click.command(help="List transformations")
@click.option("--limit", default=10, help="Number of transformations to list, defaults to 10. Use -1 to list all.")
@click.option(
    "-i", "--interactive", is_flag=True, help="Display only 10 transformations at a time, then page through them."
)
@click.pass_obj
def list(obj: Dict, limit: int = 10, interactive: bool = False) -> None:
    _, exp_client = get_clients(obj)
    try:
        transformations = exp_client.transformations.list(limit=limit)
        if interactive:
            chunks = [transformations[i : i + 10] for i in range(0, len(transformations), 10)]
            for chunk in chunks:
                click.clear()
                click.echo(print_transformations(chunk))
                ch = input("Press Enter to continue, q to quit ")
                if ch == "q":
                    return
        else:
            click.echo(print_transformations(transformations))
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
