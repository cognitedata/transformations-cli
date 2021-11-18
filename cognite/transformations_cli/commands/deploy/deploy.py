from typing import Dict, Union

import click
from cognite.client import CogniteClient as Client
from cognite.experimental.data_classes.transformations import OidcCredentials, Transformation

from cognite.transformations_cli.clients import get_clients
from cognite.transformations_cli.commands.deploy.transformation_config import (
    TransformationConfigError,
    parse_transformation_configs,
)
from cognite.transformations_cli.commands.deploy.transformations_api import (
    StandardResult,
    TupleResult,
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


def verify_oidc_credentials(type: str, credentials: OidcCredentials, cluster: str) -> None:
    token_inspect = None
    base_url = f"https://{cluster}.cognitedata.com"
    try:
        client = Client(
            base_url=base_url,
            client_name="transformations-cli-credentials-test",
            project=credentials.cdf_project_name,
            token_url=credentials.token_uri,
            token_client_id=credentials.client_id,
            token_client_secret=credentials.client_secret,
            token_scopes=credentials.scopes,
            token_custom_args={"audience": credentials.audience} if credentials.audience else None,
        )
        token_inspect = client.iam.token.inspect()
    except Exception as ex:
        raise TransformationConfigError(f"Credentials for {type} failed to validate: {str(ex)}")

    if not next((x for x in token_inspect.projects if x.url_name == credentials.cdf_project_name), None):
        raise TransformationConfigError(
            f"Credentials for {type} failed to validate: they lack projects:list and groups:list in project {credentials.cdf_project_name}"
        )


def verify_credentials(t: Transformation, cluster: str) -> None:
    if t.has_destination_oidc_credentials:
        verify_oidc_credentials(f"{t.name} write", t.destination_oidc_credentials, cluster)
    if t.has_source_oidc_credentials:
        verify_oidc_credentials(f"{t.name} read", t.source_oidc_credentials, cluster)


def print_results(
    resource_type: str, action: str, results: Union[StandardResult, TupleResult], debug: bool = False
) -> None:
    if results:
        click.echo(f"Number of {resource_type}s {action}d: {len(results)}")
        if debug:
            click.echo(f"List of {resource_type}s {action}d:")
            click.echo(results)
    return None


@click.command(help="Deploy a set of transformations from a directory")
@click.argument(
    "path",
    default=".",
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
        cluster = obj["cluster"]
        transformation_configs = parse_transformation_configs(path)
        transformations = [
            to_transformation(conf_path, transformation_configs[conf_path], cluster)
            for conf_path in transformation_configs
        ]
        transformations_ext_ids = [t.external_id for t in transformation_configs.values()]

        for t in transformations:
            verify_credentials(t, cluster)

        existing_transformations_ext_ids = get_existing_trasformation_ext_ids(exp_client, transformations_ext_ids)
        new_transformation_ext_ids = get_new_transformation_ids(
            transformations_ext_ids, existing_transformations_ext_ids
        )

        _, updated_transformations, created_transformations = upsert_transformations(
            exp_client, transformations, existing_transformations_ext_ids, new_transformation_ext_ids
        )

        print_results("transformation", "update", updated_transformations, debug)
        print_results("transformation", "create", created_transformations, debug)

        existing_schedules_dict = get_existing_schedules_dict(exp_client, transformations_ext_ids)
        existing_notifications_dict = get_existing_notifications_dict(exp_client, transformations_ext_ids)

        requested_schedules_dict = {
            t.external_id: to_schedule(t.external_id, t.schedule) for t in transformation_configs.values() if t.schedule
        }

        deleted_schedules, updated_schedules, created_schedules = upsert_schedules(
            exp_client,
            existing_schedules_dict,
            requested_schedules_dict,
            existing_transformations_ext_ids,
            new_transformation_ext_ids,
        )

        print_results("schedule", "delete", deleted_schedules, debug)
        print_results("schedule", "update", updated_schedules, debug)
        print_results("schedule", "create", created_schedules, debug)

        requested_notifications_dict = dict()
        for t in transformation_configs.values():
            if t.notifications:
                notifs = [to_notification(t.external_id, dest) for dest in t.notifications]
                requested_notifications_dict[t.external_id] = notifs

        deleted_notifications, _, created_notifications = upsert_notifications(
            exp_client,
            existing_notifications_dict,
            requested_notifications_dict,
            existing_transformations_ext_ids,
            new_transformation_ext_ids,
        )

        print_results("notification", "delete", deleted_notifications, debug)
        print_results("notification", "create", created_notifications, debug)
    except TransformationConfigError as e:
        exit(e.message)
