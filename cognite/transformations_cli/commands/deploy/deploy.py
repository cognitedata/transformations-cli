from typing import Dict

import click

from cognite.transformations_cli.commands.deploy.transformation_config import (
    ConfigParserError,
    parse_transformation_configs,
)


@click.command(help="Deploy a set of transformations from a directory")
@click.option(
    "--path",
    default=".",
    help="A directory to search for transformation manifests. If omitted, the current directory is used.",
)
@click.pass_obj
def deploy(obj: Dict, path: str) -> None:
    """
        Deploy a set of transformations from a directory
    Args:
        path (str): Root directory for transformations
    """
    click.echo(f"Deploying transformation.... cluster:{obj['cluster']}")
    try:
        parse_transformation_configs(path)
    except ConfigParserError as e:
        click.echo(e.message)
        exit(1)
