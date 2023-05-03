from dataclasses import dataclass, field
from enum import Enum
from typing import List, Literal, Optional, Union


class DestinationType(str, Enum):
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
    nodes = "nodes"
    edges = "edges"
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
class ReadOidcAuthConfig:
    client_id: Optional[str]
    client_secret: Optional[str]
    token_url: Optional[str]
    scopes: Optional[List[str]]
    cdf_project_name: Optional[str]
    audience: Optional[str]


@dataclass
class WriteOidcAuthConfig:
    client_id: Optional[str]
    client_secret: Optional[str]
    token_url: Optional[str]
    scopes: Optional[List[str]]
    cdf_project_name: Optional[str]
    audience: Optional[str]


@dataclass
class ReadWriteAuthentication:
    read: ReadOidcAuthConfig
    write: WriteOidcAuthConfig


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
class ViewInfo:
    space: str
    external_id: str
    version: Union[int, str]

    """
    CAST view version int to string
    """

    def __init__(self, space: str, external_id: str, version: Union[int, str]):
        self.space = space
        self.external_id = external_id
        self.version = str(version)


@dataclass
class EdgeType:
    space: str
    external_id: str


@dataclass
class DataModelInfo:
    space: str
    external_id: str
    version: Union[int, str]
    destination_type: str
    destination_relationship_from_type: Optional[str] = None

    """
    CAST DataModel version int to string
    """

    def __init__(
        self,
        space: str,
        external_id: str,
        version: Union[int, str],
        destination_type: str,
        destination_relationship_from_type: Optional[str] = None,
    ):
        self.space = space
        self.external_id = external_id
        self.version = str(version)
        self.destination_type = destination_type
        self.destination_relationship_from_type = destination_relationship_from_type

    def __hash__(self) -> int:
        if self.destination_relationship_from_type is not None:
            return hash(
                (
                    self.space,
                    self.external_id,
                    self.version,
                    self.destination_type,
                    self.destination_relationship_from_type,
                )
            )
        else:
            return hash((self.space, self.external_id, self.version, self.destination_type))


@dataclass
class InstanceNodesDestinationConfig:
    """
    Valid type values are: nodes
    """

    view: Optional[ViewInfo]
    instance_space: Optional[str]
    type: Literal[DestinationType.nodes] = DestinationType.nodes


@dataclass
class InstanceEdgesDestinationConfig:
    """
    Valid type values are: edges
    """

    view: Optional[ViewInfo]
    instance_space: Optional[str]
    edge_type: Optional[EdgeType]
    type: Literal[
        DestinationType.edges
    ] = DestinationType.edges  # DestinationType updated with  Literal[DestinationType.edges]


@dataclass
class InstanceDataModelDestinationConfig:
    """
    Valid type values are: instances
    """

    data_model: Optional[DataModelInfo]
    instance_space: Optional[str]
    type: Literal[DestinationType.instances] = DestinationType.instances


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
    InstanceNodesDestinationConfig,
    InstanceEdgesDestinationConfig,
    RawDestinationAlternativeConfig,
    InstanceDataModelDestinationConfig,
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
