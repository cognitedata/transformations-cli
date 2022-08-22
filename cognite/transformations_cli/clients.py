import sys
from typing import Dict

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import APIKey, OAuthClientCredentials
from cognite.client.exceptions import CogniteAPIKeyError


def get_client(obj: Dict, timeout: int = 60) -> CogniteClient:
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
            client_config = ClientConfig(
                client_name="transformations_cli",
                base_url=base_url,
                project=cdf_project_name,
                timeout=timeout,
                credentials=APIKey(api_key),
            )
        else:
            token_custom_args = {"audience": audience} if audience else {}
            client_config = ClientConfig(
                base_url=base_url,
                client_name="transformations_cli",
                project=cdf_project_name,
                timeout=timeout,
                credentials=OAuthClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret,
                    token_url=token_url,
                    scopes=scopes,
                    **token_custom_args,
                ),
            )
        return CogniteClient(client_config)
    except CogniteAPIKeyError as e:
        sys.exit(f"Cognite client cannot be initialised: {e}.")
