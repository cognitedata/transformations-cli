import logging
import sys
from typing import Dict

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import APIKey, OAuthClientCredentials
from cognite.client.exceptions import CogniteAPIError

logger = logging.getLogger(name=None)


def get_project_from_api_key(client: CogniteClient) -> str:
    project = client.login.status().project
    if not project:
        sys.exit("Invalid authentication, please check the base_url or api_key.")
    return project


def get_client(obj: Dict, timeout: int = 60) -> CogniteClient:
    api_key = obj.get("api_key")
    client_id = obj.get("client_id")
    client_secret = obj.get("client_secret")
    token_url = obj.get("token_url")
    scopes = obj.get("scopes")
    audience = obj.get("audience")
    cdf_project_name = obj.get("cdf_project_name")
    cluster = obj.get("cluster", "europe-west1-1")
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
            client = CogniteClient(client_config)
            prj = get_project_from_api_key(client)
            if not cdf_project_name:
                logger.warn("CDF project name is not provided, it will be detected using the API key.")
                client.config.project = prj
            elif prj.lower() != cdf_project_name.lower():
                sys.exit(f"API key does not grant access to the project {cdf_project_name}.")
            return client
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
    except CogniteAPIError as e:
        sys.exit(f"Cognite client cannot be initialised: {e}.")
