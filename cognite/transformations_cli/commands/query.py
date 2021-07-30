from typing import Dict

import click

from cognite.transformations_cli._clients import get_clients


@click.command(help="Make a SQL query and retrieve results")
@click.argument("query")
@click.option("--source-limit", default=100, help="number of greetings")
@click.option("--infer-schema-limit", default=100, help="number of greetings")
@click.option("--limit", default=1000, help="number of greetings")
@click.pass_obj
def query(obj: Dict, query: str) -> None:
    _, exp_client = get_clients(obj)
    click.echo(f"Querying...... cluster:{obj['cluster']}")
