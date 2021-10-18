from typing import Dict

import click

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.deploy.transformation_config import (
    TransformationConfigError,
    parse_transformation_configs,
)
from cognite.transformations_cli.commands.deploy.transformations_api import (
    to_schedule,
    to_transformation,
    upsert_notifications,
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
        _, exp_client = get_clients(obj)
        transformation_configs = parse_transformation_configs(path)
        transformations = [to_transformation(tr, obj["cluster"]) for tr in transformation_configs]
        upsert_transform(exp_client, transformations)
        schedules = []
        delete_schedules = []
        created_notifications = []
        for transform in transformation_configs:
            if transform.schedule:
                schedules.append(to_schedule(transform))
            else:
                # These will be deleted using ignore_unknown_ids
                # in case these transformations existed with a schedule before
                delete_schedules.append(transform.external_id)
            created_notifications += upsert_notifications(exp_client, transform.external_id, transform.notifications)
        upsert_schedules(exp_client, schedules, delete_schedules)
        if created_notifications:
            click.echo(f"Number of created notifications: {len(created_notifications)}")

    except TransformationConfigError as e:
        exit(e.message)
