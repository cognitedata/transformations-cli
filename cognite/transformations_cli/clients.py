import sys
from typing import Dict, Tuple

from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIKeyError
from cognite.experimental import CogniteClient as ExpCogniteClient


def get_clients(obj: Dict) -> Tuple[CogniteClient, ExpCogniteClient]:
    api_key = obj["api_key"]
    client_id = obj["client_id"]
    client_secret = obj["client_secret"]
    token_url = obj["token_url"]
    scopes = obj["scopes"]
    audience = obj["audience"]
    cdf_project_name = obj["cdf_project_name"]
    cluster = obj["cluster"]
    base_url = f"https://{cluster}.cognitedata.com"
    if not api_key and not audience:
        scopes = scopes.strip().split(" ") if scopes else [f"https://{cluster}.cognitedata.com/.default"]
    try:
        if api_key is not None and (
            client_id is not None
            or client_secret is not None
            or token_url is not None
            or scopes is not None
            or audience is not None
        ):
            sys.exit("Please provide only API key configuration or only OAuth2 configuration.")
        elif api_key is not None:
            return (
                CogniteClient(
                    client_name="transformations_cli", api_key=api_key, base_url=base_url, project=cdf_project_name
                ),
                ExpCogniteClient(
                    client_name="transformations_cli", api_key=api_key, base_url=base_url, project=cdf_project_name
                ),
            )
        else:
            return (
                CogniteClient(
                    base_url=base_url,
                    client_name="transformations_cli",
                    token_client_id=client_id,
                    token_client_secret=client_secret,
                    token_url=token_url,
                    token_scopes=scopes,
                    project=cdf_project_name,
                    token_custom_args={"audience": audience} if audience else None,
                ),
                ExpCogniteClient(
                    base_url=base_url,
                    client_name="transformations_cli",
                    token_client_id=client_id,
                    token_client_secret=client_secret,
                    token_url=token_url,
                    token_scopes=scopes,
                    project=cdf_project_name,
                    token_custom_args={"audience": audience} if audience else None,
                ),
            )
    except CogniteAPIKeyError as e:
        sys.exit(f"Cognite client cannot be initialised: {e}.")
