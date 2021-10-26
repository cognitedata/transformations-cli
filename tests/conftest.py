import os
import uuid
from typing import List

import pytest
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import (
    OidcCredentials,
    RawTable,
    Transformation,
    TransformationDestination,
)

from cognite.transformations_cli.clients import get_clients


@pytest.fixture
def valid_credentials() -> OidcCredentials:
    return OidcCredentials(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        token_uri="https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token",
        scopes="https://bluefield.cognitedata.com/.default",
        cdf_project_name="extractor-bluefield-testing",
        audience=None,
    )


@pytest.fixture
def test_transformation_ext_ids() -> List[str]:
    uuid_conf = uuid.uuid1()
    return [
        f"{uuid_conf}_cli_test1",
        f"{uuid_conf}_cli_test2",
        f"{uuid_conf}_cli_test3",
        f"{uuid_conf}_cli_test4",
    ]


@pytest.fixture
def configs_to_create(
    test_transformation_ext_ids: List[str], valid_credentials: OidcCredentials
) -> List[Transformation]:
    return [
        Transformation(
            external_id=test_transformation_ext_ids[0],
            name=test_transformation_ext_ids[0],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=TransformationDestination("assets"),
            conflict_mode="upsert",
            query="select 'asd' as name, 'asd' as externalId",
            is_public=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[1],
            name=test_transformation_ext_ids[2],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=RawTable(type="raw", database="cli-test-db", table="cli-test"),
            conflict_mode="upsert",
            query="select 'asd' as key, 'asd' as externalId",
            is_public=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[2],
            name=test_transformation_ext_ids[2],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=TransformationDestination("events"),
            conflict_mode="update",
            query="select 'asd' as externalId",
            is_public=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[3],
            name=test_transformation_ext_ids[3],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=TransformationDestination(type="timeseries"),
            conflict_mode="upsert",
            query="select 'asd' as externalId, 'asd' as name",
            is_public=True,
        ),
    ]


@pytest.fixture
def exp_client() -> ExpCogniteClient:
    obj = {
        "api_key": None,
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "token_url": "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token",
        "scopes": "https://bluefield.cognitedata.com/.default",
        "audience": None,
        "cdf_project_name": "extractor-bluefield-testing",
        "cluster": "bluefield",
    }
    return get_clients(obj)[1]
