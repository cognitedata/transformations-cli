from dataclasses import dataclass, field
from os import environ
from typing import List, Optional, Union

from cognite.transformations_cli.commands.deploy.transformation_types import (
    ActionType,
    AuthConfig,
    DestinationConfig,
    DestinationType,
    QueryConfig,
    RawDestinationConfig,
    ReadWriteAuthentication,
    TransformationConfig,
    TransformationConfigError,
)


# YamlDotNet is case insensitive on enums, for full backwards compatibility that
# needs to be reflected here
def legacy_destination_type_to_new(input: str) -> DestinationType:
    input_low = input.lower()
    for en in DestinationType:
        clean_name = en.name.replace("_", "")
        if clean_name == input_low:
            return en
    raise TransformationConfigError(f"Invalid destination type: {input}")


def legacy_action_to_new(input: str) -> ActionType:
    input_low = input.lower()
    for en in ActionType:
        if en.name == input_low:
            return en
    raise TransformationConfigError(f"Invalid action type: {input}")


@dataclass
class ReadWriteApiKeyLegacy:
    read: str
    write: str


@dataclass
class AuthConfigLegacy:
    client_id: Optional[str]
    client_secret: Optional[str]
    token_url: Optional[str]
    scopes: Optional[List[str]]
    cdf_project_name: Optional[str]
    audience: Optional[str]

    def to_new(self) -> AuthConfig:
        return AuthConfig(
            api_key=None,
            client_id=environ[self.client_id] if self.client_id is not None else None,
            audience=self.audience,
            client_secret=environ[self.client_secret] if self.client_secret is not None else None,
            token_url=self.token_url,
            scopes=self.scopes,
            cdf_project_name=self.cdf_project_name,
        )


@dataclass
class ReadWriteAuthConfigLegacy:
    read: AuthConfigLegacy
    write: AuthConfigLegacy


@dataclass
class DestinationLegacy:
    type: str
    raw_database: Optional[str] = None
    raw_table: Optional[str] = None

    def to_new(self) -> Union[RawDestinationConfig, DestinationConfig]:
        new_type = legacy_destination_type_to_new(self.type)
        if self.raw_database and self.raw_table:
            return RawDestinationConfig(raw_database=self.raw_database, raw_table=self.raw_table)
        return DestinationConfig(new_type)


@dataclass
class TransformationConfigLegacy:
    external_id: str
    name: str
    query: str
    authentication: Union[AuthConfigLegacy, ReadWriteAuthConfigLegacy, None]
    api_key: Union[str, ReadWriteApiKeyLegacy, None]
    schedule: Optional[str]
    destination: Union[str, DestinationLegacy]
    notifications: List[str] = field(default_factory=list)
    shared: bool = False
    ignore_null_fields: bool = True
    action: str = "upsert"
    legacy: bool = True

    def to_new(self) -> TransformationConfig:
        query = QueryConfig(file=self.query)
        auth = ReadWriteAuthentication(
            read=AuthConfig(None, None, None, None, None, None, None),
            write=AuthConfig(None, None, None, None, None, None, None),
        )

        if isinstance(self.authentication, ReadWriteAuthConfigLegacy):
            if self.authentication.read is not None:
                auth.read = self.authentication.read.to_new()
            if self.authentication.write is not None:
                auth.write = self.authentication.write.to_new()
        elif isinstance(self.authentication, AuthConfigLegacy):
            auth.read = auth.write = self.authentication.to_new()

        if isinstance(self.api_key, ReadWriteApiKeyLegacy):
            if self.api_key.read is not None:
                auth.read.api_key = environ[self.api_key.read]
            if self.api_key.write is not None:
                auth.write.api_key = environ[self.api_key.write]
        elif isinstance(self.api_key, str):
            auth.read.api_key = auth.write.api_key = environ[self.api_key]

        destination = (
            self.destination.to_new()
            if isinstance(self.destination, DestinationLegacy)
            else DestinationConfig(legacy_destination_type_to_new(self.destination))
        )
        action = legacy_action_to_new(self.action)

        return TransformationConfig(
            external_id=self.external_id,
            name=self.name,
            query=query,
            authentication=auth,
            destination=destination,
            notifications=self.notifications,
            shared=self.shared,
            ignore_null_fields=self.ignore_null_fields,
            action=action,
            schedule=self.schedule,
            legacy=True,
            data_set_id=None,
            data_set_external_id=None,
        )
