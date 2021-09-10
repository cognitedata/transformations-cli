import glob
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from cognite.extractorutils.configtools import InvalidConfigError, load_yaml


class DestinationType(Enum):
    assets = "assets"
    timeseries = "timeseries"
    asset_hierarchy = "asset_hierarchy"
    events = "events"
    datapoints = "datapoints"
    string_datapoints = "string_datapoints"
    sequences = "sequences"
    files = "files"
    labels = "labels"
    relationships = "relationships"
    raw = "raw"


class ActionType(Enum):
    create = "abort"
    abort = "abort"
    update = "update"
    upsert = "upsert"
    delete = "delete"


class TransformationConfigError(Exception):
    """Exception raised for config parser

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


@dataclass
class AuthConfig:
    api_key: Optional[str]
    token_client_id: Optional[str]
    token_client_secret: Optional[str]
    token_url: Optional[str]
    token_scopes: Optional[List[str]]
    token_project: Optional[str]


@dataclass
class DestinationConfig:
    """
    Valid type values are: assets, asset_hierarchy, events, timeseries, datapoints, string_datapoints, raw (needs database and table)
    """

    type: DestinationType
    database: Optional[str] = None
    table: Optional[str] = None


@dataclass
class TransformationConfig:
    """
    Master configuration class of a transformation
    """

    external_id: str
    name: str
    query: str
    authentication: Optional[AuthConfig]
    read_authentication: Optional[AuthConfig]
    write_authentication: Optional[AuthConfig]
    schedule: Optional[str]
    destination: DestinationConfig
    notifications: List[str] = field(default_factory=list)
    shared: bool = False
    ignore_null_fields: bool = True
    action: str = ActionType.upsert.value


def _validate_destination_type(config: TransformationConfig) -> None:
    if config.destination.type == DestinationType.raw and (
        config.destination.database is None or config.destination.table is None
    ):
        raise TransformationConfigError("Raw destination type requires database and table properties to be set.")
    if not hasattr(DestinationType, config.destination.type.name):
        raise TransformationConfigError(
            f"{config.destination.type} is not a valid destination type. Destination type should be one of the following: {', '.join([e.value for e in DestinationType])}"
        )


def _validate_action(config: TransformationConfig) -> None:
    if not hasattr(ActionType, config.action):
        raise TransformationConfigError(
            f"{config.action} is not a valid action type. Action should be one of the following: {', '.join([e.value for e in ActionType])}"
        )
    config.action = ActionType.abort.value if config.action == ActionType.create.value else config.action


def _validate_exclusive_auth(external_id: str, auth: Optional[AuthConfig]) -> None:
    if (
        auth
        and auth.api_key
        and (
            auth.token_client_id
            or auth.token_client_secret
            or auth.token_project
            or auth.token_scopes
            or auth.token_url
        )
    ):
        raise TransformationConfigError(f"Please provide only one of api-key or oidc credentials: {external_id}")


def _validate_auth(config: TransformationConfig) -> None:
    read_credentials: Optional[AuthConfig] = config.read_authentication
    write_credentials: Optional[AuthConfig] = config.write_authentication
    credentials: Optional[AuthConfig] = config.authentication
    if credentials and (read_credentials or write_credentials):
        raise TransformationConfigError(
            f"Please provide only one of credentials or read/write credentials set: {config.external_id}"
        )
    _validate_exclusive_auth(config.external_id, credentials)
    _validate_exclusive_auth(config.external_id, write_credentials)
    _validate_exclusive_auth(config.external_id, read_credentials)


def _validate_config(config: TransformationConfig) -> None:
    _validate_destination_type(config)
    _validate_action(config)
    _validate_auth(config)


def _parse_transformation_config(path: str) -> TransformationConfig:
    with open(path) as f:
        try:
            config: TransformationConfig = load_yaml(f, TransformationConfig)
        except InvalidConfigError as e:
            raise TransformationConfigError(e.message)
    return config


def parse_transformation_configs(base_dir: Optional[str]) -> List[TransformationConfig]:
    if base_dir is None:
        base_dir = "."

    if os.path.isdir(base_dir) is False:
        raise TransformationConfigError(f"Transformation root folder not found: {base_dir}")

    transformations: List[TransformationConfig] = []
    yaml_paths: List[str] = glob.glob(f"{base_dir}/**/*.yaml", recursive=True) + glob.glob(
        f"{base_dir}/**/*.yml", recursive=True
    )

    for file_path in yaml_paths:
        try:
            parsed_conf = _parse_transformation_config(file_path)
            _validate_config(
                parsed_conf
            )  # will modify action and destination if necessary in place and  throw exception if sth is off
            transformations.append(parsed_conf)
        except Exception as e:
            raise TransformationConfigError(
                f"Failed to parse transformation config, please check that you conform required fields and format: {e}"
            )
    return transformations
