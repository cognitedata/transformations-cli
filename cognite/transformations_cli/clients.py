from typing import Dict, Optional, Tuple

from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIKeyError
from cognite.experimental import CogniteClient as ExpCogniteClient


def _client_provider(
    cluster: Optional[str],
    api_key: Optional[str],
    token_client_id: Optional[str],
    token_client_secret: Optional[str],
    token_url: Optional[str],
    token_scopes: Optional[str],
    token_project: Optional[str],
) -> Tuple[CogniteClient, ExpCogniteClient]:
    base_url = f"https://{cluster}.cognitedata.com"
    scopes = token_scopes.strip().split(",") if token_scopes else [f"https://{cluster}.cognitedata.com/.default"]
    try:
        if api_key is not None and (
            token_client_id is not None
            or token_client_secret is not None
            or token_project is not None
            or token_url is not None
            or token_scopes is not None
        ):
            exit("Please provide only API key configuration or only OIDC configuration.")
        elif api_key is not None:
            return (
                CogniteClient(client_name="transformations_cli", api_key=api_key, base_url=base_url),
                ExpCogniteClient(client_name="transformations_cli", api_key=api_key, base_url=base_url),
            )
        else:
            return (
                CogniteClient(
                    client_name="transformations_cli",
                    token_client_id=token_client_id,
                    token_client_secret=token_client_secret,
                    token_url=token_url,
                    token_scopes=scopes,
                    project=token_project,
                ),
                ExpCogniteClient(
                    client_name="transformations_cli",
                    token_client_id=token_client_id,
                    token_client_secret=token_client_secret,
                    token_url=token_url,
                    token_scopes=scopes,
                    project=token_project,
                ),
            )
    except CogniteAPIKeyError as e:
        exit(f"Cognite client cannot be initialised: {e}.")


def get_clients(obj: Dict) -> Tuple[CogniteClient, ExpCogniteClient]:
    api_key = obj["api_key"]
    token_client_id = obj["token_client_id"]
    token_client_secret = obj["token_client_secret"]
    token_url = obj["token_url"]
    token_scopes = obj["token_scopes"]
    token_project = obj["token_project"]
    cluster = obj["cluster"]
    return _client_provider(
        cluster=cluster,
        api_key=api_key,
        token_client_id=token_client_id,
        token_client_secret=token_client_secret,
        token_url=token_url,
        token_scopes=token_scopes,
        token_project=token_project,
    )
