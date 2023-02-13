import os
import sys
from typing import Dict, List, Optional, Tuple, Union

from cognite.client import CogniteClient
from cognite.client.data_classes import (
    OidcCredentials,
    Transformation,
    TransformationDestination,
    TransformationNotification,
    TransformationSchedule,
    TransformationUpdate,
)
from cognite.client.data_classes.transformations.common import DataModelInstances, Instances, SequenceRows
from cognite.client.exceptions import CogniteAPIError, CogniteDuplicatedError, CogniteNotFoundError

from cognite.transformations_cli.commands.deploy.transformation_types import (
    ActionType,
    AuthConfig,
    DestinationConfig,
    DestinationConfigType,
    DMIDestinationConfig,
    InstancesDestinationConfig,
    QueryConfig,
    RawDestinationAlternativeConfig,
    RawDestinationConfig,
    ReadWriteAuthentication,
    ScheduleConfig,
    SequenceRowsDestinationConfig,
    TransformationConfig,
)
from cognite.transformations_cli.commands.utils import chunk_items, exit_with_cognite_api_error

TupleResult = List[Tuple[str, str]]
StandardResult = List[str]


def to_transformation(
    client: CogniteClient, conf_path: str, config: TransformationConfig, cluster: str = "europe-west1-1"
) -> Transformation:
    return Transformation(
        name=config.name,
        external_id=config.external_id,
        destination=to_destination(config.destination),
        conflict_mode=to_action(config.action),
        is_public=config.shared,
        ignore_null_fields=config.ignore_null_fields,
        query=to_query(conf_path, config.query),
        source_api_key=to_read_api_key(config.authentication),
        destination_api_key=to_write_api_key(config.authentication),
        source_oidc_credentials=to_read_oidc(config.authentication, cluster),
        destination_oidc_credentials=to_write_oidc(config.authentication, cluster),
        data_set_id=to_data_set_id(client, config.data_set_id, config.data_set_external_id),
        tags=config.tags,
    )


def to_data_set_id(
    client: CogniteClient, data_set_id: Optional[int], data_set_external_id: Optional[str]
) -> Optional[int]:
    err = ""
    if data_set_external_id:
        try:
            data_set = client.data_sets.retrieve(external_id=data_set_external_id)
        except CogniteAPIError as e:
            err = f" ({e})"
            data_set = None
        if data_set:
            return data_set.id
        else:
            sys.exit(
                f"Invalid data set external id, please verify if it exists or you have the required capability: {data_set_external_id}{err}"
            )
    return data_set_id


def to_action(action: ActionType) -> str:
    return "abort" if action == ActionType.create else action.value


def to_destination(destination: DestinationConfigType) -> TransformationDestination:
    if isinstance(destination, DestinationConfig):
        return TransformationDestination(destination.type.value)
    elif isinstance(destination, RawDestinationConfig):
        return TransformationDestination.raw(destination.raw_database, destination.raw_table)
    elif isinstance(destination, RawDestinationAlternativeConfig):
        return TransformationDestination.raw(destination.database, destination.table)
    elif isinstance(destination, SequenceRowsDestinationConfig):
        return SequenceRows(destination.external_id)
    elif isinstance(destination, DMIDestinationConfig):
        return DataModelInstances(
            destination.model_external_id, destination.space_external_id, destination.instance_space_external_id
        )
    elif isinstance(destination, InstancesDestinationConfig):
        return Instances(
            destination.view_external_id,
            destination.view_version,
            destination.view_space_external_id,
            destination.instance_space_external_id,
        )
    else:
        return TransformationDestination(destination.value)


def to_query(conf_path: str, query: Union[str, QueryConfig]) -> str:
    try:
        dir_path = os.path.dirname(conf_path)
        if isinstance(query, QueryConfig):
            sql_path = os.path.join(dir_path, query.file)
            with open(sql_path, "r") as f:
                return f.read()
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
        return " ".join(scopes)
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


def to_schedule(transformation_external_id: str, schedule: Union[str, ScheduleConfig]) -> TransformationSchedule:
    if isinstance(schedule, ScheduleConfig):
        interval = schedule.interval
        is_paused = schedule.is_paused
    else:
        interval = schedule
        is_paused = False
    return TransformationSchedule(external_id=transformation_external_id, interval=interval, is_paused=is_paused)


def to_notification(transformation_external_id: str, destination: str) -> TransformationNotification:
    return TransformationNotification(transformation_external_id=transformation_external_id, destination=destination)


def get_existing_transformation_ext_ids(client: CogniteClient, all_ext_ids: List[str]) -> List[str]:
    return [
        t.external_id
        for t in client.transformations.retrieve_multiple(external_ids=all_ext_ids, ignore_unknown_ids=True)
    ]


def get_new_transformation_ids(all_ext_ids: List[str], existig_ext_ids: List[str]) -> List[str]:
    return list(set(all_ext_ids) - set(existig_ext_ids))


def get_existing_schedules_dict(client: CogniteClient, all_ext_ids: List[str]) -> Dict[str, TransformationSchedule]:
    return {
        s.external_id: s
        for s in client.transformations.schedules.retrieve_multiple(external_ids=all_ext_ids, ignore_unknown_ids=True)
    }


def get_existing_notifications_dict(
    client: CogniteClient, all_ext_ids: List[str]
) -> Dict[str, List[TransformationNotification]]:
    existing_notifications = dict()
    for ext_id in all_ext_ids:
        notifications = client.transformations.notifications.list(transformation_external_id=ext_id, limit=-1)
        if notifications:
            existing_notifications[ext_id] = notifications
    return existing_notifications


def upsert_transformations(
    client: CogniteClient,
    transformations: List[Transformation],
    existing_ext_ids: List[str],
    new_ext_ids: List[str],
) -> Tuple[StandardResult, StandardResult, StandardResult]:
    try:
        items_to_update = [tr for tr in transformations if tr.external_id in existing_ext_ids]
        items_to_create = [tr for tr in transformations if tr.external_id in new_ext_ids]

        for u in chunk_items(items_to_update):
            client.transformations.update(u)
            # Partial update for data set id to be able to clear data set id field when requested.
            dataset_update = [
                # Clear data set id if it is not provided, else set data set id with a new value
                TransformationUpdate(external_id=du.external_id).data_set_id.set(du.data_set_id)
                for du in u
            ]
            client.transformations.update(dataset_update)
        for c in chunk_items(items_to_create):
            client.transformations.create(c)
        return [], [t.external_id for t in items_to_update], [t.external_id for t in items_to_create]
    except (CogniteDuplicatedError, CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
    return [], [], []


def upsert_schedules(
    client: CogniteClient,
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

        for d in chunk_items(to_delete):
            client.transformations.schedules.delete(external_id=d)
        schedules_update_list = [requested_schedules_dict[ext_id] for ext_id in to_update]
        for u in chunk_items(schedules_update_list):
            client.transformations.schedules.update(u)
        schedules_create_list = [requested_schedules_dict[ext_id] for ext_id in to_create]
        for c in chunk_items(schedules_create_list):
            client.transformations.schedules.create(c)
    except (CogniteDuplicatedError, CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
    return to_delete, to_update, to_create


def upsert_notifications(
    client: CogniteClient,
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
        to_delete_external_ids = list(to_delete.keys())

        for d in chunk_items(to_delete_external_ids):
            client.transformations.notifications.delete(d)
        for c in chunk_items(to_create):
            client.transformations.notifications.create(c)
        return (
            [to_delete[key] for key in to_delete],
            [],
            [(n.transformation_external_id, n.destination) for n in to_create],
        )
    except (CogniteDuplicatedError, CogniteNotFoundError, CogniteAPIError) as e:
        exit_with_cognite_api_error(e)
    return [], [], []
