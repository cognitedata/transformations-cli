from typing import Dict, List, Optional

import click
from cognite.client.data_classes import TransformationJob
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_client
from cognite.transformations_cli.commands.utils import (
    exit_with_cognite_api_error,
    is_id_exclusive,
    paginate,
    print_jobs,
)


def log_jobs(id_str: Optional[str], items: List[TransformationJob]) -> None:
    if id_str:
        click.echo(f"Resulting jobs for transformation with {id_str}:")
    click.echo(print_jobs(items))


@click.command(help="Show latest jobs for a given transformation")
@click.option("--id", help="List jobs by transformation id. Either this or --external-id must be specified.")
@click.option("--external-id", help="List jobs by transformation external_id. Either this or --id must be specified.")
@click.option("--limit", default=10, help="Limit for the job history, defaults to 10. Use -1 to retrieve all results.")
@click.option("-i", "--interactive", is_flag=True, help="Display only 10 jobs at a time, paging through them.")
@click.pass_obj
def jobs(obj: Dict, id: Optional[int], external_id: Optional[str], limit: int = 10, interactive: bool = False) -> None:
    client = get_client(obj)
    is_id_exclusive(id, external_id)
    try:
        id_str = None
        if id:
            id = int(id)
            id_str = f"id {id}"
        if external_id:
            id_str = f"external_id {external_id}"

        if id_str:
            click.echo(f"Listing the latest jobs for transformation with {id_str}:")
        else:
            click.echo("Listing the latest jobs for all transformations:")

        jobs = client.transformations.jobs.list(
            limit=limit, transformation_id=id, transformation_external_id=external_id
        )

        if jobs:
            if interactive:
                paginate(jobs, lambda chunk: log_jobs(id_str, chunk))
            else:
                log_jobs(id_str, jobs)
        else:
            click.echo("No jobs to list.")
    except (CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
