import os
from typing import List

import click
from cognite.client.exceptions import CogniteAPIError, CogniteDuplicatedError
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes import TransformationNotification
from cognite.experimental.data_classes.transformation_schedules import TransformationSchedule
from cognite.experimental.data_classes.transformations import (
    OidcCredentials,
    RawTable,
    Transformation,
    TransformationDestination,
)

from cognite.transformations_cli.commands.deploy.transformation_config import (
    AuthConfig,
    DestinationType,
    TransformationConfig,
)


def to_transformation(config: TransformationConfig, cluster: str = "europe-west1-1") -> Transformation:
    if config.destination.type == DestinationType.raw:
        destination = RawTable("raw", config.destination.raw_database, config.destination.raw_table)
    else:
        destination = TransformationDestination(config.destination.type.name)
    read_api_key = None
    write_api_key = None
    read_oidc = None
    write_oidc = None
    if config.authentication:
        auth = config.authentication
        read_api_key = get_api_key(auth)
        write_api_key = get_api_key(auth)
        read_oidc = get_oidc(auth, cluster) if not read_api_key else None
        write_oidc = get_oidc(auth, cluster) if not write_api_key else None
    elif config.read_authentication:
        auth = config.read_authentication
        read_api_key = get_api_key(auth)
        read_oidc = get_oidc(auth, cluster) if not read_api_key else None
    elif config.write_authentication:
        auth = config.write_authentication
        write_api_key = get_api_key(auth)
        write_oidc = get_oidc(auth, cluster) if not write_api_key else None

    return Transformation(
        name=config.name,
        external_id=config.external_id,
        destination=destination,
        conflict_mode=config.action.value,
        is_public=config.shared,
        ignore_null_fields=config.ignore_null_fields,
        query=config.query,
        source_api_key=read_api_key,
        destination_api_key=write_api_key,
        source_oidc_credentials=read_oidc,
        destination_oidc_credentials=write_oidc,
    )


def get_api_key(auth: AuthConfig) -> str:
    return os.environ.get(auth.api_key, auth.api_key)


def get_oidc(auth: AuthConfig, cluster: str) -> OidcCredentials:
    scopes = ",".join(auth.scopes) if auth.token_scopes else f"https://{cluster}.cognitedata.com/.default"
    return OidcCredentials(auth.token_client_id, auth.token_client_secret, scopes, auth.token_url, auth.token_project)


def to_schedule(config: TransformationConfig) -> TransformationSchedule:
    return TransformationSchedule(external_id=config.external_id, interval=config.schedule)


def to_notifications(config: TransformationConfig) -> List[TransformationNotification]:
    return [
        TransformationNotification(config_external_id=config.external_id, destination=n.destination)
        for n in config.notifications
    ]


# TODO use retrieve_multiple as in schedules when implemented in sdk
def upsert_transform(exp_client: ExpCogniteClient, transformations: List[Transformation]) -> None:
    all_ext_ids = [tr.external_id for tr in transformations]
    multiple_ids = [x for x in all_ext_ids if all_ext_ids.count(x) > 1]
    if multiple_ids:
        exit(f"Following external_id's are used multiple times, please fix them: {multiple_ids}")
    try:
        created_transforms = exp_client.transformations.create(transformations)
    except CogniteDuplicatedError as e:
        update_ext_ids = set([dup["externalId"] for dup in e.duplicated])
        create_ext_ids = set(all_ext_ids) - update_ext_ids
        update_items = [tr for tr in transformations if tr.external_id in update_ext_ids]
        create_items = [tr for tr in transformations if tr.external_id in create_ext_ids]
        updated_transforms = exp_client.transformations.update(update_items)
        created_transforms = exp_client.transformations.create(create_items)
        if updated_transforms:
            click.echo(f"Number of updated transformations: {len(updated_transforms)}")
            click.echo(
                f"external_id's of updated transformations: {', '.join([tr.external_id for tr in updated_transforms])}"
            )
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
    if created_transforms:
        click.echo(f"Number of created transformations: {len(created_transforms)}")
        click.echo(
            f"external_id's of created transformations: {', '.join([tr.external_id for tr in created_transforms])}"
        )


# TODO delete schedules when ommitted
def upsert_schedules(exp_client: ExpCogniteClient, schedules: List[TransformationSchedule]) -> None:
    try:
        all_ext_ids = [s.external_id for s in schedules]
        existing_schedules = exp_client.transformations.schedules.retrieve_multiple(
            external_ids=all_ext_ids, ignore_unknown_ids=True
        )

        existing_ext_ids = [item.external_id for item in existing_schedules]
        new_ext_ids = set([s.external_id for s in schedules]) - set(existing_ext_ids)

        existing_items = [s for s in schedules if s.external_id in existing_ext_ids]
        new_items = [s for s in schedules if s.external_id in new_ext_ids]

        updated_schedules = exp_client.transformations.schedules.update(existing_items)
        created_schedules = exp_client.transformations.schedules.create(new_items)
        if updated_schedules:
            click.echo(f"Number of updated schedules: {len(updated_schedules)}")
            click.echo(f"external_id's of updated schedules: {', '.join([tr.external_id for tr in updated_schedules])}")
        if created_schedules:
            click.echo(f"Number of created schedules: {len(created_schedules)}")
            click.echo(f"external_id's of created schedules: {', '.join([tr.external_id for tr in created_schedules])}")
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")


# TODO delete notifications when ommitted
def create_notifications(exp_client: ExpCogniteClient, notifications: List[TransformationNotification]) -> None:
    try:
        exp_client.transformations.notifications.create(notifications)
    except CogniteDuplicatedError as e:
        dup_ids = [n["id"] for n in e.duplicated]
        dup_ext_ids = [n["externalId"] for n in e.duplicated]
        notifications = [
            n
            for n in notifications
            if n.transformation_id not in dup_ids and n.transformation_external_id not in dup_ext_ids
        ]
        exp_client.transformations.notifications.create(notifications)
    except CogniteAPIError as e:
        exit(f"Cognite API error has occurred: {e}")
