from typing import Dict, Optional

import click

from cognite.transformations_cli._clients import get_clients


@click.command(help="Delete a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.pass_obj
def delete(obj: Dict, id: Optional[int], external_id: Optional[str]) -> None:
    _, exp_client = get_clients(obj)
    click.echo(f"Deleting a transformation......  cluster:{obj['cluster']}")
