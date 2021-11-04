import sys
from typing import Dict, List, Optional, Tuple, Union

from cognite.client.exceptions import CogniteAPIError, CogniteDuplicatedError, CogniteNotFoundError
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes import TransformationNotification
from cognite.experimental.data_classes.transformation_schedules import TransformationSchedule
from cognite.experimental.data_classes.transformations import (
    OidcCredentials,
    RawTable,
    Transformation,
    TransformationDestination,
)

from cognite.transformations_cli.commands.deploy.transformation_types import (
    ActionType,
    AuthConfig,
    DestinationConfig,
    DestinationType,
    QueryConfig,
    ReadWriteAuthentication,
    TransformationConfig,
)
from cognite.transformations_cli.commands.utils import exit_with_cognite_api_error

TupleResult = List[Tuple[str, str]]
StandardResult = List[str]


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
        return RawTable("raw", destination.raw_database, destination.raw_table)
    return TransformationDestination(destination.type.value)


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


def stringify_scopes(scopes: Optional[List[str]]) -> Optional[str]:
    if scopes:
        " ".join(scopes)
    return None


def get_default_scopes(scopes: Optional[str], cluster: str) -> str:
    return scopes if scopes else f"https://{cluster}.cognitedata.com/.default"


def is_oidc_defined(auth_config: AuthConfig) -> bool:
    return (
        auth_config.client_id and auth_config.client_secret and auth_config.token_url and auth_config.cdf_project_name
    )


def get_oidc(auth_config: AuthConfig, cluster: str) -> Optional[OidcCredentials]:
    stringified_scopes = stringify_scopes(auth_config.scopes)
    scopes = stringified_scopes if auth_config.audience else get_default_scopes(stringified_scopes, cluster)
    return (
        OidcCredentials(
            client_id=auth_config.client_id,
            client_secret=auth_config.client_secret,
            scopes=scopes,
            token_uri=auth_config.token_url,
            cdf_project_name=auth_config.cdf_project_name,
            audience=auth_config.audience,
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


def to_schedule(transformation_external_id: str, interval: str) -> TransformationSchedule:
    return TransformationSchedule(external_id=transformation_external_id, interval=interval)


def to_notification(transformation_external_id: str, destination: str) -> TransformationNotification:
    return TransformationNotification(transformation_external_id=transformation_external_id, destination=destination)


def get_existing_trasformation_ext_ids(exp_client: ExpCogniteClient, all_ext_ids: List[str]) -> List[str]:
    return [
        t.external_id
        for t in exp_client.transformations.retrieve_multiple(external_ids=all_ext_ids, ignore_unknown_ids=True)
    ]


def get_new_transformation_ids(all_ext_ids: List[str], existig_ext_ids: List[str]) -> List[str]:
    return list(set(all_ext_ids) - set(existig_ext_ids))


def get_existing_schedules_dict(
    exp_client: ExpCogniteClient, all_ext_ids: List[str]
) -> Dict[str, TransformationSchedule]:
    return {
        s.external_id: s
        for s in exp_client.transformations.schedules.retrieve_multiple(
            external_ids=all_ext_ids, ignore_unknown_ids=True
        )
    }


def get_existing_notifications_dict(
    exp_client: ExpCogniteClient, all_ext_ids: List[str]
) -> Dict[str, List[TransformationNotification]]:
    existing_notifications = dict()
    for ext_id in all_ext_ids:
        notifications = exp_client.transformations.notifications.list(transformation_external_id=ext_id, limit=-1)
        if notifications:
            existing_notifications[ext_id] = notifications
    return existing_notifications


def upsert_transformations(
    exp_client: ExpCogniteClient,
    transformations: List[Transformation],
    existing_ext_ids: List[str],
    new_ext_ids: List[str],
) -> Tuple[StandardResult, StandardResult, StandardResult]:
    try:
        updated = exp_client.transformations.update(
            [tr for tr in transformations if tr.external_id in existing_ext_ids]
        )
        created = exp_client.transformations.create([tr for tr in transformations if tr.external_id in new_ext_ids])
        return [], [t.external_id for t in updated], [t.external_id for t in created]
    except (CogniteDuplicatedError, CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
    return [], [], []


def upsert_schedules(
    exp_client: ExpCogniteClient,
    existing_schedules_dict: Dict[str, TransformationSchedule],
    requested_schedules_dict: Dict[str, TransformationSchedule],
    existing_transformations_ext_ids: List[str],
    new_transformations_ext_ids: List[str],
) -> Tuple[StandardResult, StandardResult, StandardResult]:
    to_delete = []
    to_update = []
    to_create = []
    try:
        for ext_id in existing_transformations_ext_ids:
            if ext_id in existing_schedules_dict and ext_id not in requested_schedules_dict:
                to_delete.append(ext_id)
            elif ext_id in existing_schedules_dict:
                to_update.append(ext_id)
            elif ext_id in requested_schedules_dict:
                to_create.append(ext_id)
        to_create += [ext_id for ext_id in new_transformations_ext_ids if ext_id in requested_schedules_dict]
        exp_client.transformations.schedules.delete(external_id=to_delete)
        exp_client.transformations.schedules.update([requested_schedules_dict[ext_id] for ext_id in to_update])
        exp_client.transformations.schedules.create([requested_schedules_dict[ext_id] for ext_id in to_create])
    except (CogniteDuplicatedError, CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
    return to_delete, to_update, to_create


def upsert_notifications(
    exp_client: ExpCogniteClient,
    existing_notifications_dict: Dict[str, List[TransformationNotification]],
    requested_notifications_dict: Dict[str, List[TransformationNotification]],
    existing_transformations_ext_ids: List[str],
    new_transformations_ext_ids: List[str],
) -> Tuple[TupleResult, TupleResult, TupleResult]:
    try:
        to_delete = dict()
        to_create = []
        for ext_id in new_transformations_ext_ids:
            if ext_id in requested_notifications_dict:
                to_create += requested_notifications_dict[ext_id]

        for ext_id in existing_transformations_ext_ids:
            existing_notif = existing_notifications_dict.get(ext_id, [])
            requested_notif = requested_notifications_dict.get(ext_id, [])
            existing_destinations = [e.destination for e in existing_notif]
            requested_destinations = [e.destination for e in requested_notif]

            to_delete.update(
                {e.id: (ext_id, e.destination) for e in existing_notif if e.destination not in requested_destinations}
            )
            to_create += [e for e in requested_notif if e.destination not in existing_destinations]
        exp_client.transformations.notifications.delete(list(to_delete.keys()))
        exp_client.transformations.notifications.create(to_create)
        return (
            [to_delete[key] for key in to_delete],
            [],
            [(n.transformation_external_id, n.destination) for n in to_create],
        )
    except (CogniteDuplicatedError, CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
    return [], [], []
