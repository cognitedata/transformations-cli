from typing import Dict

import click

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.deploy.transformation_config import (
    TransformationConfigError,
    parse_transformation_configs,
)
from cognite.transformations_cli.commands.deploy.utils import (
    create_notifications,
    to_notifications,
    to_schedule,
    to_transformation,
    upsert_schedules,
    upsert_transform,
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
    click.echo("Deploying transformation...")
    try:
        transformation_configs = parse_transformation_configs(path)
        transformations = [to_transformation(tr, obj["cluster"]) for tr in transformation_configs]
        _, exp_client = get_clients(obj)
        upsert_transform(exp_client, transformations)
        schedules = []
        notifications = []
        for transform in transformation_configs:
            if transform.schedule:
                schedules.append(to_schedule(transform))
            if transform.notifications:
                notifications = to_notifications(transform)
        create_notifications(exp_client, notifications)
        upsert_schedules(exp_client, schedules)
    except TransformationConfigError as e:
        exit(e.message)
