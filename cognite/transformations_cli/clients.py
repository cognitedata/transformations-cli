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
    base_url = f"https://{cluster}.cognitedata.com"
    # Removing API Key
    if not audience:
        scopes = scopes.strip().split(" ") if scopes else [f"https://{cluster}.cognitedata.com/.default"]
    try:
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
    except CogniteAPIError as e:
        sys.exit(f"Cognite client cannot be initialised: {e}.")
