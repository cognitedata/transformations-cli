import os
from contextlib import nullcontext as does_not_raise
from typing import Dict, Optional

import pytest
from cognite.client import CogniteClient
from cognite.client.data_classes import TransformationList
from cognite.client.exceptions import CogniteReadTimeout

from cognite.transformations_cli.clients import disable_env_var, enable_env_var, get_client


def clean_up_env_vars(name: str, old_val: Optional[str]) -> None:
    if old_val:
        enable_env_var(name, old_val)
    else:
        del os.environ[name]


def test_ignore_sdk_auth_environment_variables_api_key(obj: Dict) -> None:
    # disable and get the values from old environment variables to recover later in case other tests are using it.
    old_env = disable_env_var("COGNITE_API_KEY")
    os.environ["COGNITE_API_KEY"] = os.environ["API_KEY"]

    client = get_client(obj)
    res = client.transformations.list(limit=1)
    assert type(res) == TransformationList

    # Test if the environment variable is recovered after get_client
    # COGNITE_API_KEY is picked up and used
    client2 = CogniteClient(client_name="emel")
    res2 = client2.transformations.list(limit=1)
    assert type(res2) == TransformationList

    # recover the values before the other tests
    clean_up_env_vars("COGNITE_API_KEY", old_env)


def test_ignore_sdk_auth_environment_variables(obj: Dict) -> None:
    # disable and get the values from old environment variables to recover later in case other tests are using it.
    old_project = disable_env_var("COGNITE_PROJECT")
    old_id = disable_env_var("COGNITE_CLIENT_ID")
    old_secret = disable_env_var("COGNITE_CLIENT_SECRET")
    old_token_url = disable_env_var("COGNITE_TOKEN_URL")
    old_scopes = disable_env_var("COGNITE_TOKEN_SCOPES")

    os.environ["COGNITE_PROJECT"] = obj["cdf_project_name"]
    os.environ["COGNITE_CLIENT_ID"] = obj["client_id"]
    os.environ["COGNITE_CLIENT_SECRET"] = obj["client_secret"]
    os.environ["COGNITE_TOKEN_URL"] = obj["token_url"]
    os.environ["COGNITE_TOKEN_SCOPES"] = obj["scopes"]

    new_obj = {"api_key": os.environ["API_KEY"], "cluster": "api", "cdf_timeout": 60}
    client = get_client(new_obj)
    res = client.transformations.list(limit=1)
    assert type(res) == TransformationList

    # Test if the environment variable is recovered after get_client
    # COGNITE_CLIENT_ID, COGNITE_CLIENT_SECRET and such are picked up and used
    client2 = CogniteClient(base_url=f"https://{obj['cluster']}.cognitedata.com", client_name="emel")
    res2 = client2.transformations.list(limit=1)
    assert type(res2) == TransformationList

    # recover the values before the other tests
    clean_up_env_vars("COGNITE_PROJECT", old_project)
    clean_up_env_vars("COGNITE_CLIENT_ID", old_id)
    clean_up_env_vars("COGNITE_CLIENT_SECRET", old_secret)
    clean_up_env_vars("COGNITE_TOKEN_URL", old_token_url)
    clean_up_env_vars("COGNITE_TOKEN_SCOPES", old_scopes)


def test_timeout(obj: Dict) -> None:
    new_obj = dict(obj)
    new_obj["cdf_timeout"] = 0.1
    client = get_client(new_obj)
    with pytest.raises(CogniteReadTimeout):
        client.transformations.preview("select * from _cdf.assets limit 1000")

    # original fixture has 60 secs timeout
    client2 = get_client(obj)
    with does_not_raise():
        client2.transformations.preview("select * from _cdf.assets limit 1000")
