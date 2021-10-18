import sys
from typing import List, Optional, Union

import click
from cognite.client.exceptions import CogniteAPIError
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
from cognite.transformations_cli.commands.utils import exit_with_cognite_api_error


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


def to_notification(transformation_external_id: str, destination: str) -> TransformationNotification:
    return TransformationNotification(transformation_external_id=transformation_external_id, destination=destination)


def upsert_transform(exp_client: ExpCogniteClient, transformations: List[Transformation]) -> None:
    try:
        all_ext_ids = [s.external_id for s in transformations]
        existing_transformations = exp_client.transformations.retrieve_multiple(
            external_ids=all_ext_ids, ignore_unknown_ids=True
        )

        existing_ext_ids = [item.external_id for item in existing_transformations]
        new_ext_ids = set([s.external_id for s in transformations]) - set(existing_ext_ids)

        existing_items = [s for s in transformations if s.external_id in existing_ext_ids]
        new_items = [s for s in transformations if s.external_id in new_ext_ids]

        updated_transformations = exp_client.transformations.update(existing_items)
        created_transformations = exp_client.transformations.create(new_items)
        if updated_transformations:
            click.echo(f"Number of updated transformations: {len(updated_transformations)}")
            click.echo(
                f"external_id's of updated transformations: {', '.join([tr.external_id for tr in updated_transformations])}"
            )
        if created_transformations:
            click.echo(f"Number of created transformations: {len(created_transformations)}")
            click.echo(
                f"external_id's of created transformations: {', '.join([tr.external_id for tr in created_transformations])}"
            )
        return None
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)


def upsert_schedules(
    exp_client: ExpCogniteClient, schedules: List[TransformationSchedule], no_schedules: List[str]
) -> None:
    try:
        exp_client.transformations.schedules.delete(external_id=no_schedules, ignore_unknown_ids=True)

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
        return None
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)


def upsert_notifications(
    exp_client: ExpCogniteClient, external_id: str, destinations: List[str]
) -> List[TransformationNotification]:
    try:
        existing_notifications = exp_client.transformations.notifications.list(transformation_external_id=external_id)
        existing_destinations = set([n.destination for n in existing_notifications])
        destinations_to_deploy = set(destinations)
        new_destinations = list(destinations_to_deploy - existing_destinations)
        destinations_to_delete = list(existing_destinations - destinations_to_deploy)
        new_notifications = [to_notification(external_id, dest) for dest in new_destinations]
        created_notifications = exp_client.transformations.notifications.create(new_notifications)
        exp_client.transformations.notifications.delete(
            id=[n.id for n in existing_notifications if n.destination in destinations_to_delete]
        )
        return created_notifications
    except CogniteAPIError as e:
        exit_with_cognite_api_error(e)
        return []
