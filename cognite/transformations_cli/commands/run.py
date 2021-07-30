from typing import Dict, Optional

import click

from cognite.transformations_cli._clients import get_clients


@click.command(help="Start and/or watch transformation jobs")
@click.option("--id", help="The id of the transformation to run. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to run. Either this or --id must be specified."
)
@click.option("--watch", is_flag=True, help="Wait until job has completed")
@click.option(
    "--watch-only",
    is_flag=True,
    help="Do not start a transformation job, only watch the most recent job for completion",
)
@click.option(
    "--time-out", default=(12 * 60 * 60), help="Maximum amount of time to wait for job to complete in seconds"
)
@click.pass_obj
def run(
    obj: Dict,
    id: Optional[int],
    external_id: Optional[str],
    watch: Optional[bool],
    watch_only: Optional[bool],
    time_out: Optional[int],
) -> None:
    _, exp_client = get_clients(obj)
    click.echo(f"Running transformation..... cluster:{obj['cluster']}")
