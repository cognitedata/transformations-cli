from typing import Dict, Optional

import click

from cognite.transformations_cli.clients import get_clients


@click.command(help="Start and/or watch transformation jobs")
@click.option("--id", help="The id of the transformation to run. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to run. Either this or --id must be specified."
)
@click.option("--watch", is_flag=True, help="Wait until job has completed")
# @click.option(
#     "--watch-only",
#     is_flag=True,
#     help="Do not start a transformation job, only watch the most recent job for completion",
# )
# @click.option(
#     "--time-out", default=(12 * 60 * 60), help="Maximum amount of time to wait for job to complete in seconds"
# )
# TODO format before printing
@click.pass_obj
def run(
    obj: Dict,
    id: Optional[int],
    external_id: Optional[str],
    watch: bool = False,
    # watch_only: bool = False, // Waiting for Jaime to support list jobs by transform_id
    # time_out: Optional[int], // Asked Jaime if we should support time_out on wait
) -> None:
    _, exp_client = get_clients(obj)
    if id and external_id:
        exit("Please only provide one of id and external id.")
    if id:
        job = exp_client.transformations.run(transformation_id=id, watch=watch)
    elif external_id:
        job = exp_client.transformations.run(transformation_external_id=external_id, watch=watch)
    click.echo("Job details:")
    click.echo(job)
