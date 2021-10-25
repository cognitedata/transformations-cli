from typing import Optional

import click
from click import Context

from cognite.transformations_cli import __version__
from cognite.transformations_cli.commands.delete import delete
from cognite.transformations_cli.commands.deploy.deploy import deploy
from cognite.transformations_cli.commands.jobs import jobs
from cognite.transformations_cli.commands.list import list
from cognite.transformations_cli.commands.query import query
from cognite.transformations_cli.commands.run import run
from cognite.transformations_cli.commands.show import show


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(prog_name="transformations_cli", version=__version__)
@click.option(
    "--cluster",
    default="europe-west1-1",
    help="The CDF cluster where Transformations is hosted (e.g. greenfield, europe-west1-1)",
    envvar="TRANSFORMATIONS_CLUSTER",
)
@click.option(
    "--api-key",
    help="API key to interact with transformations API. Provide this or make sure to set 'TRANSFORMATIONS_API_KEY' environment variable if you want to authenticate with API keys.",
    envvar="TRANSFORMATIONS_API_KEY",
)
@click.option(
    "--client-id",
    help="Client ID to interact with transformations API. Provide this or make sure to set 'TRANSFORMATIONS_CLIENT_ID' environment variable if you want to authenticate with OAuth2.",
    envvar="TRANSFORMATIONS_CLIENT_ID",
)
@click.option(
    "--client-secret",
    help="Client secret to interact with transformations API. Provide this or make sure to set 'TRANSFORMATIONS_CLIENT_SECRET' environment variable if you want to authenticate with OAuth2.",
    envvar="TRANSFORMATIONS_CLIENT_SECRET",
)
@click.option(
    "--token-url",
    help="Token URL to interact with transformations API. Provide this or make sure to set 'TRANSFORMATIONS_TOKEN_URL' environment variable if you want to authenticate with OAuth2.",
    envvar="TRANSFORMATIONS_TOKEN_URL",
)
@click.option(
    "--scopes",
    help="Scopes to interact with transformations API, relevant for OAuth2 authentication method. 'TRANSFORMATIONS_SCOPES' environment variable can be used instead.",
    envvar="TRANSFORMATIONS_SCOPES",
)
@click.option(
    "--audience",
    help="Audience to interact with transformations API, relevant for OAuth2 authentication method. 'TRANSFORMATIONS_AUDIENCE' environment variable can be used instead.",
    envvar="TRANSFORMATIONS_AUDIENCE",
)
@click.option(
    "--cdf-project-name",
    help="Project to interact with transformations API, 'TRANSFORMATIONS_PROJECT' environment variable can be used instead. Required for OAuth2 and optional for api-keys.",
    envvar="TRANSFORMATIONS_PROJECT",
)
@click.pass_context
def transformations_cli(
    context: Context,
    cluster: str = "europe-west1-1",
    api_key: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    token_url: Optional[str] = None,
    scopes: Optional[str] = None,
    audience: Optional[str] = None,
    cdf_project_name: Optional[str] = None,
) -> None:
    context.obj = {
        "cluster": cluster,
        "api_key": api_key,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_url": token_url,
        "scopes": scopes,
        "audience": audience,
        "cdf_project_name": cdf_project_name,
    }


transformations_cli.add_command(deploy)
transformations_cli.add_command(run)
transformations_cli.add_command(query)
transformations_cli.add_command(list)
transformations_cli.add_command(show)
transformations_cli.add_command(jobs)
transformations_cli.add_command(delete)
