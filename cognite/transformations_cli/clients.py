import os
import sys
from typing import Dict, Optional

from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIKeyError

from cognite.transformations_cli.commands import DEFAULT_TIMEOUT


def disable_env_var(env_var_name: str) -> Optional[str]:
    default_val = os.getenv(env_var_name)
    if os.environ.get(env_var_name):
        print("")
        del os.environ[env_var_name]
    return default_val


def enable_env_var(env_var_name: str, env_var_val: Optional[str]) -> None:
    if env_var_val:
        os.environ[env_var_name] = env_var_val


def get_client(obj: Dict) -> CogniteClient:
    api_key = obj.get("api_key")
    client_id = obj.get("client_id")
    client_secret = obj.get("client_secret")
    token_url = obj.get("token_url")
    scopes = obj.get("scopes")
    audience = obj.get("audience")
    cdf_project_name = obj.get("cdf_project_name")
    cluster = obj.get("cluster", "api")
    base_url = f"https://{cluster}.cognitedata.com"
    timeout = float(obj.get("cdf_timeout", DEFAULT_TIMEOUT))

    # Small hack to prevent user's Cognite related environment variables being picked up by CogniteClient.
    default_cognite_project = disable_env_var("COGNITE_PROJECT")
    default_api_key = disable_env_var("COGNITE_API_KEY")
    default_client_id = disable_env_var("COGNITE_CLIENT_ID")
    default_client_secret = disable_env_var("COGNITE_CLIENT_SECRET")
    default_token_url = disable_env_var("COGNITE_TOKEN_URL")
    default_token_scopes = disable_env_var("COGNITE_TOKEN_SCOPES")

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
            client = CogniteClient(
                client_name="transformations_cli",
                api_key=api_key,
                base_url=base_url,
                project=cdf_project_name,
                timeout=timeout,
            )
        else:
            client = CogniteClient(
                base_url=base_url,
                client_name="transformations_cli",
                token_client_id=client_id,
                token_client_secret=client_secret,
                token_url=token_url,
                token_scopes=scopes,
                project=cdf_project_name,
                token_custom_args={"audience": audience} if audience else None,
                timeout=timeout,
            )
        enable_env_var("COGNITE_PROJECT", default_cognite_project)
        enable_env_var("COGNITE_API_KEY", default_api_key)
        enable_env_var("COGNITE_CLIENT_ID", default_client_id)
        enable_env_var("COGNITE_CLIENT_SECRET", default_client_secret)
        enable_env_var("COGNITE_TOKEN_URL", default_token_url)
        enable_env_var("COGNITE_TOKEN_SCOPES", default_token_scopes)
        return client
    except CogniteAPIKeyError as e:
        sys.exit(f"Cognite client cannot be initialised: {e}.")
