import os

from cognite.client import CogniteClient

from cognite.transformations_cli.clients import get_client, get_project_from_api_key


def test_api_key_client() -> None:
    obj = {"api_key": os.environ["JETFIRETEST_API_KEY"]}
    client = get_client(obj)
    assert get_project_from_api_key(client) == "jetfiretest"


def test_oidc_client(client: CogniteClient) -> None:
    assert len(client.iam.token.inspect().projects) >= 1
