import os
import uuid
from typing import Dict, List

import pytest
from click.testing import CliRunner
from cognite.client import CogniteClient
from cognite.client.data_classes import DataSet, OidcCredentials, Transformation, TransformationDestination

from cognite.transformations_cli.clients import get_client


@pytest.fixture
def client_id() -> str:
    return os.environ["CLIENT_ID"]


@pytest.fixture
def client_secret() -> str:
    return os.environ["CLIENT_SECRET"]


@pytest.fixture
def token_uri() -> str:
    return "https://login.microsoftonline.com/b86328db-09aa-4f0e-9a03-0136f604d20a/oauth2/v2.0/token"


@pytest.fixture
def scopes() -> str:
    return "https://bluefield.cognitedata.com/.default"


@pytest.fixture
def cdf_project_name() -> str:
    return "extractor-bluefield-testing"


@pytest.fixture
def cluster() -> str:
    return "bluefield"


@pytest.fixture
def valid_credentials(
    client_id: str, client_secret: str, token_uri: str, scopes: str, cdf_project_name: str
) -> OidcCredentials:
    return OidcCredentials(
        client_id=client_id,
        client_secret=client_secret,
        token_uri=token_uri,
        scopes=scopes,
        cdf_project_name=cdf_project_name,
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
def new_dataset(client: CogniteClient) -> DataSet:
    ds_ext_id1 = "cli-transformation-ds"
    ds1 = client.data_sets.retrieve(external_id=ds_ext_id1)
    if not ds1:
        data_set1 = DataSet(name=ds_ext_id1, external_id=ds_ext_id1)
        ds1 = client.data_sets.create(data_set1)
    yield ds1


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
            destination=TransformationDestination.assets(),
            conflict_mode="upsert",
            query="select 'asd' as name, 'asd' as externalId",
            is_public=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[1],
            name=test_transformation_ext_ids[1],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=TransformationDestination.raw(database="cli-test-db", table="cli-test"),
            conflict_mode="upsert",
            query="select 'asd' as key, 'asd' as externalId",
            is_public=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[2],
            name=test_transformation_ext_ids[2],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=TransformationDestination.events(),
            conflict_mode="update",
            query="select 'asd' as externalId",
            is_public=True,
        ),
        Transformation(
            external_id=test_transformation_ext_ids[3],
            name=test_transformation_ext_ids[3],
            source_oidc_credentials=valid_credentials,
            destination_oidc_credentials=valid_credentials,
            destination=TransformationDestination.timeseries(),
            conflict_mode="upsert",
            query="select 'asd' as externalId 'asd' as name",
            is_public=True,
        ),
    ]


@pytest.fixture
def obj(client_id: str, client_secret: str, token_uri: str, scopes: str, cluster: str, cdf_project_name: str) -> Dict:
    return {
        "api_key": None,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_url": token_uri,
        "scopes": scopes,
        "audience": None,
        "cdf_project_name": cdf_project_name,
        "cluster": cluster,
        "cdf_timeout": 60,
    }


@pytest.fixture
def client(obj: Dict) -> CogniteClient:
    return get_client(obj)


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()
