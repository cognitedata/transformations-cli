from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    get_id_from_external_id,
    is_id_exclusive,
    print_jobs,
)


@click.command(help="Show latest jobs for a given transformation")
@click.option("--id", help="List jobs by transformation id. Either this or --external-id must be specified.")
@click.option("--external-id", help="List jobs by transformation external_id. Either this or --id must be specified.")
@click.option("--limit", default=10, help="Limit for the job history, defaults to 10. Use -1 to retrieve all results.")
@click.pass_obj
def jobs(obj: Dict, id: Optional[int], external_id: Optional[str], limit: int = 10) -> None:
    _, exp_client = get_clients(obj)
    is_id_exclusive(id, external_id)
    try:
        if id:
            click.echo(f"Listing the latest jobs for transformation with id {id}:")
        if external_id:
            id = get_id_from_external_id(exp_client=exp_client, external_id=external_id)
            click.echo(f"Listing the latest jobs for transformation with external_id {external_id}:")
        jobs = exp_client.transformations.jobs.list(limit=limit, transformation_id=id)
        if jobs:
            click.echo("Resulting jobs:")
            click.echo(print_jobs(jobs))
        else:
            click.echo("No jobs to list.")
    except (CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
