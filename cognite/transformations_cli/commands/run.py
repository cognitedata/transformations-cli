from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    exit_with_id_not_found,
    is_id_exclusive,
)


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
# TODO format before printing
@click.pass_obj
def run(
    obj: Dict,
    id: Optional[int],
    external_id: Optional[str],
    watch: bool = False,
    watch_only: bool = False,
    timeout: Optional[int] = None,
) -> None:
    _, exp_client = get_clients(obj)
    is_id_exclusive(id, external_id)
    try:
        if not watch_only:
            job = exp_client.transformations.run(transformation_id=id, id=id, watch=watch, timeout=timeout)
        else:
            if external_id:
                id = exp_client.transformations.retrieve(external_id=external_id).id
            jobs = exp_client.transformations.jobs.list(transformation_id=id)
            job = jobs[0].wait(timeout=timeout) if jobs else None
        click.echo("Job details:")
        click.echo(job)
    except CogniteNotFoundError as e:
        exit_with_id_not_found(e)
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
