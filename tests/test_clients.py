from cognite.client import CogniteClient


def test_oidc_client(client: CogniteClient) -> None:
    assert len(client.iam.token.inspect().projects) >= 1
