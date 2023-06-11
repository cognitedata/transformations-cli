import logging
import sys
from typing import Dict

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.exceptions import CogniteAPIError

logger = logging.getLogger(name=None)

def get_client(obj: Dict, timeout: int = 60) -> CogniteClient:
    client_id = obj.get("client_id")
    client_secret = obj.get("client_secret")
    token_url = obj.get("token_url")
    scopes = obj.get("scopes")
    audience = obj.get("audience")
    cdf_project_name = obj.get("cdf_project_name")
    cluster = obj.get("cluster", "europe-west1-1")
    base_url = obj.get("base_url")
    token_custom_args_str = obj.get("token_custom_args")
    if base_url is None or len(base_url) == 0:
        base_url = f"https://{cluster}.cognitedata.com"
    if not audience:
        scopes = scopes.strip().split(" ") if scopes else [f"{base_url}/.default"]
    try:
        token_custom_args = {}
        if token_custom_args_str:
            for pair in token_custom_args_str.split(","):
                key, value = pair.split("=")
                # remove any whitespace around the key & convert to lower case
                key = key.strip().lower()
                # remove any whitespace around the value
                value = value.strip()
                token_custom_args[key] = value
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
                audience=audience,
                **token_custom_args,
            ),
        )
        return CogniteClient(client_config)
    except CogniteAPIError as e:
        sys.exit(f"Cognite client cannot be initialised: {e}.")
