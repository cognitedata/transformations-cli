import sys
from typing import List, Optional, Union

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
    ActionType,
    AuthConfig,
    DestinationConfig,
    DestinationType,
    QueryConfig,
    ReadWriteAuthentication,
    TransformationConfig,
)


def to_transformation(config: TransformationConfig, cluster: str = "europe-west1-1") -> Transformation:
    return Transformation(
        name=config.name,
        external_id=config.external_id,
        destination=to_destination(config.destination),
        conflict_mode=to_action(config.action),
        is_public=config.shared,
        ignore_null_fields=config.ignore_null_fields,
        query=to_query(config.query),
        source_api_key=to_read_api_key(config.authentication),
        destination_api_key=to_write_api_key(config.authentication),
        source_oidc_credentials=to_read_oidc(config.authentication, cluster),
        destination_oidc_credentials=to_write_oidc(config.authentication, cluster),
    )


def to_action(action: ActionType) -> str:
    return "abort" if action == ActionType.create else action.value


def to_destination(destination: DestinationConfig) -> TransformationDestination:
    if destination.type == DestinationType.raw:
        destination = RawTable("raw", destination.raw_database, destination.raw_table)
    else:
        destination = TransformationDestination(destination.type.value)


def to_query(query: Union[str, QueryConfig]) -> str:
    try:
        if isinstance(query, QueryConfig):
            with open(query.file, "r") as f:
                return f.read().replace("\n", "")
        return query
    except:
        sys.exit("Please provide a valid path for sql file.")


def to_read_api_key(authentication: Union[AuthConfig, ReadWriteAuthentication]) -> Optional[str]:
    if isinstance(authentication, AuthConfig):
        return authentication.api_key
    if isinstance(authentication, ReadWriteAuthentication):
        return authentication.read.api_key
    return None


def to_write_api_key(authentication: Union[AuthConfig, ReadWriteAuthentication]) -> Optional[str]:
    if isinstance(authentication, AuthConfig):
        return authentication.api_key
    if isinstance(authentication, ReadWriteAuthentication):
        return authentication.write.api_key
    return None


def get_default_scopes(scopes: Optional[List[str]], cluster: str) -> str:
    return ",".join(scopes) if scopes else f"https://{cluster}.cognitedata.com/.default"


def is_oidc_defined(auth_config: AuthConfig) -> bool:
    return (
        auth_config.token_client_id
        and auth_config.token_client_secret
        and auth_config.token_url
        and auth_config.token_project
    )


def get_oidc(auth_config: AuthConfig, cluster: str) -> Optional[OidcCredentials]:
    scopes = auth_config.token_scopes if auth_config.audience else get_default_scopes(auth_config.token_scopes, cluster)
    return (
        OidcCredentials(
            auth_config.token_client_id,
            auth_config.token_client_secret,
            scopes,
            auth_config.token_url,
            auth_config.token_project,
            auth_config.audience,
        )
        if is_oidc_defined(auth_config)
        else None
    )


def to_read_oidc(authentication: Union[AuthConfig, ReadWriteAuthentication], cluster: str) -> Optional[OidcCredentials]:
    return (
        get_oidc(authentication, cluster)
        if isinstance(authentication, AuthConfig)
        else get_oidc(authentication.read, cluster)
    )


def to_write_oidc(
    authentication: Union[AuthConfig, ReadWriteAuthentication], cluster: str
) -> Optional[OidcCredentials]:
    return (
        get_oidc(authentication, cluster)
        if isinstance(authentication, AuthConfig)
        else get_oidc(authentication.write, cluster)
    )


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
