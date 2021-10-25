import glob
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union

from cognite.extractorutils.configtools import load_yaml


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
    data_sets = "data_sets"


class ActionType(Enum):
    create = "create"
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
    client_id: Optional[str]
    client_secret: Optional[str]
    token_url: Optional[str]
    scopes: Optional[List[str]]
    cdf_project_name: Optional[str]
    audience: Optional[str]


@dataclass
class ReadWriteAuthentication:
    read: AuthConfig
    write: AuthConfig


@dataclass
class DestinationConfig:
    """
    Valid type values are: assets, asset_hierarchy, events, timeseries, datapoints, string_datapoints, raw (needs database and table)
    """

    type: DestinationType
    raw_database: Optional[str] = None
    raw_table: Optional[str] = None


@dataclass
class QueryConfig:
    file: str


@dataclass
class TransformationConfig:
    """
    Master configuration class of a transformation
    """

    external_id: str
    name: str
    query: Union[str, QueryConfig]
    authentication: Union[AuthConfig, ReadWriteAuthentication]
    read_authentication: Optional[AuthConfig]
    write_authentication: Optional[AuthConfig]
    schedule: Optional[str]
    destination: DestinationConfig
    notifications: List[str] = field(default_factory=list)
    shared: bool = False
    ignore_null_fields: bool = True
    action: ActionType = ActionType.upsert


def _validate_destination_type(external_id: str, destination_type: DestinationConfig) -> None:
    if destination_type.type == DestinationType.raw and (
        destination_type.raw_database is None or destination_type.raw_table is None
    ):
        raise Exception(f"Raw destination type requires database and table properties to be set: {external_id}")
    return None


def _validate_exclusive_auth(external_id: str, auth: Optional[AuthConfig]) -> None:
    if (
        auth
        and auth.api_key
        and (auth.client_id or auth.client_secret or auth.cdf_project_name or auth.scopes or auth.token_url)
    ):
        raise Exception(f"Please provide only one of api-key or OAuth2 credentials: {external_id}")
    return None


def _validate_auth(external_id: str, auth_config: Union[AuthConfig, ReadWriteAuthentication]) -> None:
    if isinstance(auth_config, AuthConfig):
        _validate_exclusive_auth(external_id, auth_config)
    if isinstance(auth_config, ReadWriteAuthentication):
        _validate_exclusive_auth(external_id, auth_config.read)
        _validate_exclusive_auth(external_id, auth_config.write)


def _validate_config(config: TransformationConfig) -> None:
    _validate_destination_type(config.external_id, config.destination)
    _validate_auth(config.external_id, config.authentication)


def _parse_transformation_config(path: str) -> TransformationConfig:
    with open(path) as f:
        return load_yaml(f, TransformationConfig, case_style="camel")


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
            # This will raise exceptions if invalid
            _validate_config(parsed_conf)
            transformations.append(parsed_conf)
        except Exception as e:
            raise TransformationConfigError(
                f"Failed to parse transformation config, please check that you conform required fields and format: {e}"
            )
    return transformations
