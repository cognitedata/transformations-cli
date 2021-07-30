from typing import Dict

import click

from cognite.transformations_cli._clients import get_clients


@click.command(help="List transformations")
@click.option("--limit", default=25, help="Number of transformations to list")
@click.pass_obj
def list(obj: Dict, limit: int) -> None:
    _, exp_client = get_clients(obj)
    limit = 25 if not limit else limit
    click.echo(exp_client.transformations.list(limit=limit))
