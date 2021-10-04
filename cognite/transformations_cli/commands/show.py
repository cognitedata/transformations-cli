from typing import Dict, Optional

import click
from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import (
    check_exclusive_id,
    exit_with_cognite_api_error,
    exit_with_id_not_found,
)


@click.command(help="Show detalis of a transformation")
@click.option("--id", help="The id of the transformation to show. Either this or --external-id must be specified.")
@click.option(
    "--external-id", help="The externalId of the transformation to show. Either this or --id must be specified."
)
@click.option(
    "--job", help="The id of the job to show. Include this to show job details instead of transformation details."
)
@click.pass_obj
# TODO format before printing
def show(obj: Dict, id: Optional[int], external_id: Optional[str], job: Optional[int]) -> None:
    _, exp_client = get_clients(obj)
    check_exclusive_id(id, external_id)
    try:
        tr = exp_client.transformations.retrieve(id=id, external_id=external_id)
        click.echo("Transformation details:")
        click.echo(tr)
    except CogniteNotFoundError as e:
        exit_with_id_not_found(e)
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
