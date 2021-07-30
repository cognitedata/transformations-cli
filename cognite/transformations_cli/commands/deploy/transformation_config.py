import glob
import os
from dataclasses import dataclass
from typing import List, Optional

from cognite.extractorutils.configtools import CogniteConfig, InvalidConfigError, load_yaml

from cognite.transformations_cli.commands.deploy.enum_definitions import ActionType, DestinationType


class ConfigParserError(Exception):
    """Exception raised for config parser

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


@dataclass
class AuthenticationConfig:
    """
    Authentication configuration of a transformation
    """

    configuration: Optional[CogniteConfig]
    read_configuration: Optional[CogniteConfig]
    write_configuration: Optional[CogniteConfig]


@dataclass
class DestinationConfig:
    """
    Valid type values are: assets, assethierarchy, events, timeseries, datapoints, stringdatapoints, raw (needs database and table)
    """

    type: str
    raw_type: Optional[str] = None
    database: Optional[str] = None
    table: Optional[str] = None


@dataclass
class TransformationConfig:
    """
    Master configuration class of a transformation
    """

    external_id: str
    name: str
    authentication: Optional[AuthenticationConfig]
    schedule: Optional[str]
    destination: DestinationConfig
    notifications: Optional[List[str]]
    shared: bool = False
    ignore_null_fields: bool = True
    action: str = ActionType.upsert


def _validate_destination_type(config: TransformationConfig) -> None:
    if config.destination.type in [DestinationType.raw, DestinationType.raw_table] and (
        config.destination.database is None or config.destination.table is None
    ):
        raise ConfigParserError("Raw destination type requires database and table properties to be set.")
    if not hasattr(DestinationType, config.destination.type):
        raise ConfigParserError(
            f"{config.destination.type} is not a valid destination type. Destination type should be one of the following: {', '.join([e.value for e in DestinationType])}"
        )
    config.destination.type = (
        DestinationType.raw_table if config.destination.type == DestinationType.raw else config.destination.type
    )
    config.destination.raw_type = "plain_raw" if config.destination.type == DestinationType.raw_table else None


def _validate_action(config: TransformationConfig) -> None:
    if not hasattr(ActionType, config.action):
        raise ConfigParserError(
            f"{config.action} is not a valid action type. Action should be one of the following: {', '.join([e.value for e in ActionType])}"
        )
    config.action = ActionType.abort if config.action == ActionType.create else config.action


def _parse_transformation_config(path: str) -> TransformationConfig:
    with open(path) as f:
        try:
            config: TransformationConfig = load_yaml(f, TransformationConfig)
        except InvalidConfigError as e:
            raise ConfigParserError(e.message)
    _validate_destination_type(config)
    _validate_action(config)
    return config


def parse_transformation_configs(base_dir: Optional[str]) -> List[TransformationConfig]:
    if base_dir is None:
        base_dir = "."

    if os.path.isdir(base_dir) is False:
        raise ConfigParserError(f"Transformation root folder not found: {base_dir}")

    transformation_configs: List[TransformationConfig] = []
    yaml_paths: List[str] = glob.glob(f"{base_dir}/**/*.yaml", recursive=True) + glob.glob(
        f"{base_dir}/**/*.yml", recursive=True
    )

    for file_path in yaml_paths:
        try:
            transformation_configs.append(_parse_transformation_config(file_path))
        except Exception as e:
            raise ConfigParserError(
                f"Failed to parse transformation config, please check that you conform required fields and format: {e}"
            )
    return transformation_configs
