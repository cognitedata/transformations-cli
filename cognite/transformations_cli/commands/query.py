from typing import Dict

import click
from cognite.client.exceptions import CogniteAPIError

from cognite.transformations_cli.clients import get_client
from cognite.transformations_cli.commands.utils import exit_with_cognite_api_error, print_query


@click.command(help="Make a SQL query and retrieve results")
@click.argument("query")
@click.option(
    "--source-limit", default=100, help="This limits the number of rows to read from each data source, defaults to 100."
)
@click.option("--infer-schema-limit", default=100, help="Schema inference limit, defaults to 100.")
@click.option(
    "--limit", default=1000, help=" This is equivalent to a final LIMIT clause on your query. Defaults to 1000."
)
@click.pass_obj
def query(obj: Dict, query: str, source_limit: int = 100, infer_schema_limit: int = 100, limit: int = 1000) -> None:
    try:
        client = get_client(obj)
        src_lim = "all" if source_limit == -1 else source_limit  # TODO Until handled in SDK
        res = client.transformations.preview(
            query=query, source_limit=src_lim, infer_schema_limit=infer_schema_limit, limit=limit
        )
        click.echo(print_query(query, res))
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
