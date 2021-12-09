from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


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
class ScheduleConfig:
    interval: str
    is_paused: bool = False


@dataclass
class TransformationConfig:
    """
    Master configuration class of a transformation
    """

    external_id: str
    name: str
    query: Union[str, QueryConfig]
    authentication: Union[AuthConfig, ReadWriteAuthentication]
    schedule: Optional[Union[str, ScheduleConfig]]
    destination: Union[DestinationType, DestinationConfig]
    notifications: List[str] = field(default_factory=list)
    shared: bool = True
    ignore_null_fields: bool = True
    action: ActionType = ActionType.upsert
    legacy: bool = False


class TransformationConfigError(Exception):
    """Exception raised for config parser

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
