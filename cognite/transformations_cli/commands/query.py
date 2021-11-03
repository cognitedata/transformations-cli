from typing import Dict

import click
from cognite.client.exceptions import CogniteAPIError

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.utils import print_query


@click.command(help="Make a SQL query and retrieve results")
@click.argument("query")
@click.option("--source-limit", default=100, help="number of greetings")
@click.option("--infer-schema-limit", default=100, help="number of greetings")
@click.option("--limit", default=1000, help="number of greetings")
@click.pass_obj
def query(obj: Dict, query: str, source_limit: int = 100, infer_schema_limit: int = 100, limit: int = 100) -> None:
    try:
        _, exp_client = get_clients(obj)
        res = exp_client.transformations.preview(
            query=query, source_limit=source_limit, infer_schema_limit=infer_schema_limit, limit=limit
        )
        click.echo(print_query(query, res))
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
