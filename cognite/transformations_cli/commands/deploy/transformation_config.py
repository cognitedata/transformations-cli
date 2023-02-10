import glob
import os
from typing import Dict, List, Optional, Union

from regex import regex

from cognite.transformations_cli.commands.deploy.load_yaml import load_yaml
from cognite.transformations_cli.commands.deploy.transformation_types import (
    AuthConfig,
    DestinationConfig,
    DestinationConfigType,
    DestinationType,
    ReadWriteAuthentication,
    TransformationConfig,
    TransformationConfigError,
)
from cognite.transformations_cli.commands.deploy.transformation_types_legacy import TransformationConfigLegacy


def _validate_destination_type(external_id: str, destination_type: DestinationConfigType) -> None:
    flat_destination_type = destination_type if isinstance(destination_type, DestinationType) else destination_type.type
    # DestinationConfig and DestinationType cannot be used for the types such as raw and sequence_rows
    if isinstance(destination_type, DestinationConfig) or isinstance(destination_type, DestinationType):
        if flat_destination_type == DestinationType.raw:
            raise Exception(
                f"Error on transformation manifest with external ID {external_id}: \
                            Raw destination type requires database and table properties to be set."
            )
        if flat_destination_type == DestinationType.data_model_instances:
            raise Exception(
                f"Error on transformation manifest with external ID {external_id}: Data model instances destination requires model_external_id,  \
                            space_external_id and instance_space_external_id to be set."
            )
        if flat_destination_type == DestinationType.instances:
            raise Exception(
                f"Error on transformation manifest with external ID {external_id}: Instances destination requires view_external_id,  \
                            view_version, view_space_external_id and instance_space_external_id to be set."
            )
        if flat_destination_type == DestinationType.sequence_rows:
            raise Exception(
                f"Error on transformation manifest with external ID {external_id}: Sequence rows destination requires external_id to be set."
            )
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


def _validate_data_set_id(data_set_id: Optional[int], data_set_external_id: Optional[str]) -> None:
    if data_set_id and data_set_external_id:
        raise Exception("Please provide only one of data_set_id or data_set_external_id")


def _validate_config(config: TransformationConfig) -> None:
    _validate_destination_type(config.external_id, config.destination)
    _validate_auth(config.external_id, config.authentication)
    _validate_data_set_id(config.data_set_id, config.data_set_external_id)


def _parse_transformation_config(path: str, legacy_mode: bool = False) -> TransformationConfig:
    r = regex.compile(r"^legacy:\s*true\s*$", flags=regex.MULTILINE | regex.IGNORECASE)
    with open(path) as f:
        data = f.read()
        if legacy_mode or r.search(data) is not None:
            legacy_config = load_yaml(data, TransformationConfigLegacy, case_style="camel")
            return legacy_config.to_new()
        else:
            return load_yaml(data, TransformationConfig, case_style="camel")


def parse_transformation_configs(base_dir: Optional[str], legacy_mode: bool = False) -> Dict[str, TransformationConfig]:
    if base_dir is None:
        base_dir = "."

    if os.path.isdir(base_dir) is False:
        raise TransformationConfigError(f"Transformation root folder not found: {base_dir}")

    transformations: Dict[str, TransformationConfig] = dict()
    yaml_paths: List[str] = glob.glob(f"{base_dir}/**/*.yaml", recursive=True) + glob.glob(
        f"{base_dir}/**/*.yml", recursive=True
    )

    for file_path in yaml_paths:
        try:
            parsed_conf = _parse_transformation_config(file_path, legacy_mode)
            # This will raise exceptions if invalid
            _validate_config(parsed_conf)
            transformations[file_path] = parsed_conf
        except Exception as e:
            raise TransformationConfigError(
                f"Failed to parse transformation config, please check that you conform required fields and format: {e}"
            )
    return transformations
