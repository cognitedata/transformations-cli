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
    sequence_rows = "sequence_rows"
    data_model_instances = "data_model_instances"
    instances = "instances"


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
    Valid type values are: assets, asset_hierarchy, events, timeseries, datapoints, string_datapoints
    """

    type: DestinationType


@dataclass
class RawDestinationConfig:
    """
    Valid type values are: raw
    """

    raw_database: str
    raw_table: str
    type: DestinationType = DestinationType.raw


@dataclass
class RawDestinationAlternativeConfig:
    """
    Valid type values are: raw
    """

    database: str
    table: str
    type: DestinationType = DestinationType.raw


@dataclass
class DMIDestinationConfig:
    """
    Valid type values are: data_model_instances
    """

    model_external_id: str
    space_external_id: str
    instance_space_external_id: str
    type: DestinationType = DestinationType.data_model_instances


@dataclass
class InstancesDestinationConfig:
    """
    Valid type values are: instances
    """

    view_external_id: str
    view_version: str
    view_space_external_id: str
    instance_space_external_id: str
    type: DestinationType = DestinationType.instances


@dataclass
class SequenceRowsDestinationConfig:
    """
    Valid type values are: sequence_rows
    """

    external_id: str
    type: DestinationType = DestinationType.sequence_rows


DestinationConfigType = Union[
    DestinationType,
    DestinationConfig,
    RawDestinationConfig,
    SequenceRowsDestinationConfig,
    DMIDestinationConfig,
    InstancesDestinationConfig,
    RawDestinationAlternativeConfig,
]


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
    destination: DestinationConfigType
    data_set_id: Optional[int]
    data_set_external_id: Optional[str]
    notifications: List[str] = field(default_factory=list)
    shared: bool = True
    ignore_null_fields: bool = True
    action: ActionType = ActionType.upsert
    legacy: bool = False
    tags: List[str] = field(default_factory=list)


class TransformationConfigError(Exception):
    """Exception raised for config parser

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
