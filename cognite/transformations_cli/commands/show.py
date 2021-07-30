from typing import Dict, Optional

import click

from cognite.transformations_cli._clients import get_clients


@click.command(help="Show detalis of a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.option(
    "--job", help="The id of the job to show. Include this to show job details instead of transformation details."
)
@click.pass_obj
def show(obj: Dict, id: Optional[int], external_id: Optional[str], job: Optional[int]) -> None:
    _, exp_client = get_clients(obj)
    click.echo(f"Showing the details of transformations...... cluster:{obj['cluster']}")
