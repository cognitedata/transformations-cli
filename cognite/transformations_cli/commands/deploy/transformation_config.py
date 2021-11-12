import glob
import os
from typing import Dict, List, Optional, Union

from cognite.extractorutils.configtools import load_yaml
from regex import regex

from cognite.transformations_cli.commands.deploy.transformation_types import (
    AuthConfig,
    DestinationConfig,
    DestinationType,
    ReadWriteAuthentication,
    TransformationConfig,
    TransformationConfigError,
)
from cognite.transformations_cli.commands.deploy.transformation_types_legacy import TransformationConfigLegacy


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
    r = regex.compile(r"^legacy:\s*true\s*$", flags=regex.MULTILINE | regex.IGNORECASE)
    with open(path) as f:
        data = f.read()
        if r.search(data) is not None:
            legacy = load_yaml(data, TransformationConfigLegacy, case_style="camel")
            return legacy.to_new()
        else:
            return load_yaml(data, TransformationConfig, case_style="camel")


def parse_transformation_configs(base_dir: Optional[str]) -> Dict[str, TransformationConfig]:
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
            parsed_conf = _parse_transformation_config(file_path)
            # This will raise exceptions if invalid
            _validate_config(parsed_conf)
            transformations[file_path] = parsed_conf
        except Exception as e:
            raise TransformationConfigError(
                f"Failed to parse transformation config, please check that you conform required fields and format: {e}"
            )
    return transformations
