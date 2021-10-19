from typing import Dict

import click

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.deploy.transformation_config import (
    TransformationConfigError,
    parse_transformation_configs,
)
from cognite.transformations_cli.commands.deploy.transformations_api import (
    get_existing_notifications_dict,
    get_existing_schedules_dict,
    get_existing_trasformation_ext_ids,
    get_new_transformation_ids,
    to_notification,
    to_schedule,
    to_transformation,
    upsert_notifications,
    upsert_schedules,
    upsert_transformations,
)


@click.command(help="Deploy a set of transformations from a directory")
@click.option(
    "--path",
    default=".",
    help="A directory to search for transformation manifests. If omitted, the current directory is used.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Print updated, created, deleted external IDs ",
)
@click.pass_obj
def deploy(obj: Dict, path: str, debug: bool = False) -> None:
    """
        Deploy a set of transformations from a directory
    Args:
        path (str): Root directory for transformations
    """
    click.echo("Deploying transformation...")
    try:
        _, exp_client = get_clients(obj)
        transformation_configs = parse_transformation_configs(path)
        transformations = [to_transformation(t) for t in transformation_configs]
        transformations_ext_ids = [t.external_id for t in transformation_configs]

        existing_transformations_ext_ids = get_existing_trasformation_ext_ids(exp_client, transformations_ext_ids)
        new_transformation_ext_ids = get_new_transformation_ids(
            transformations_ext_ids, existing_transformations_ext_ids
        )

        existing_schedules_dict = get_existing_schedules_dict(exp_client, transformations_ext_ids)
        existing_notifications_dict = get_existing_notifications_dict(exp_client, transformations_ext_ids)

        requested_schedules_dict = {
            t.external_id: to_schedule(t.external_id, t.schedule) for t in transformation_configs if t.schedule
        }
        requested_notifications_dict = dict()
        for t in transformation_configs:
            if t.notifications:
                notifs = [to_notification(t.external_id, dest) for dest in t.notifications]
                requested_notifications_dict[t.external_id] = notifs

        _, updated_transformations, created_transformations = upsert_transformations(
            exp_client, transformations, existing_transformations_ext_ids, new_transformation_ext_ids
        )

        deleted_schedules, updated_schedules, created_schedules = upsert_schedules(
            exp_client,
            existing_schedules_dict,
            requested_schedules_dict,
            existing_transformations_ext_ids,
            new_transformation_ext_ids,
        )

        deleted_notifications, _, created_notifications = upsert_notifications(
            exp_client,
            existing_notifications_dict,
            requested_notifications_dict,
            existing_transformations_ext_ids,
            new_transformation_ext_ids,
        )

        if updated_transformations:
            click.echo(f"Number of transformations updated: {len(updated_transformations)}")
            if debug:
                click.echo("List of transformations updated:")
                click.echo(updated_transformations)
        if created_transformations:
            click.echo(f"Number of transformations created: {len(created_transformations)}")
            if debug:
                click.echo("List of transformations created:")
                click.echo(created_transformations)
        if deleted_schedules:
            click.echo(f"Number of schedules deleted: {len(deleted_schedules)}")
            if debug:
                click.echo("List of schedules deleted:")
                click.echo(deleted_schedules)
        if updated_schedules:
            click.echo(f"Number of schedules updated: {len(updated_schedules)}")
            if debug:
                click.echo("List of schedules updated:")
                click.echo(updated_schedules)
        if created_schedules:
            click.echo(f"Number of schedules created: {len(created_schedules)}")
            if debug:
                click.echo("List of schedules created:")
                click.echo(created_schedules)
        if deleted_notifications:
            click.echo(f"Number of notificatons deleted: {len(deleted_notifications)}")
            if debug:
                click.echo("List of notifications deleted:")
                click.echo(deleted_notifications)
        if created_notifications:
            click.echo(f"Number of notifications created: {len(created_notifications)}")
            if debug:
                click.echo("List of notifications created:")
                click.echo(created_notifications)
    except TransformationConfigError as e:
        exit(e.message)
