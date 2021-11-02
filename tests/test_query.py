from typing import Dict, Optional

from click.testing import CliRunner
from cognite.experimental import CogniteClient as ExpCogniteClient

from cognite.transformations_cli.commands.query import query
from cognite.transformations_cli.commands.utils import print_query


def test_query(
    exp_client: ExpCogniteClient,
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
) -> None:
    example_query = "select 'cli_test' as name, 'cli_test2' as externalId, 1 as dataSetId, now() as startTime"
    api_result = exp_client.transformations.preview(query=example_query)
    cli_result = cli_runner.invoke(query, [example_query], obj=obj)

    assert cli_result.exit_code == 0
    # Remove start time from the output to compare, query specific processing.
    cli_result = cli_result.output.replace("\n", " ").split(" ")[:-10]
    cli_result = [c for c in cli_result if c]  # remove empty strings
    api_result = print_query(example_query, api_result).replace("\n", " ").split(" ")[:-10]
    api_result = [c for c in api_result if c]  # remove empty strings
    assert set(cli_result) == set(api_result)
