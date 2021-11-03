from typing import Dict, Optional

from click.testing import CliRunner

from cognite.transformations_cli.commands.query import query
from tests.helpers import from_table


def test_query(
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
) -> None:
    example_query = "select 'cli_test' as name, 'cli_test2' as externalId, 1 as dataSetId, now() as startTime"
    cli_result = cli_runner.invoke(query, [example_query], obj=obj)
    cli_result_list = from_table(cli_result.output)

    assert cli_result.exit_code == 0
    assert len(cli_result_list) == 14
    assert cli_result_list[6] == ["name", "type", "nullable"]
    assert cli_result_list[7] == ["name", "string", "False"]
    assert cli_result_list[8] == ["externalId", "string", "False"]
    assert cli_result_list[9] == ["dataSetId", "integer", "False"]
    assert cli_result_list[10] == ["startTime", "timestamp", "False"]
    assert cli_result_list[13][:-2] == ["cli_test", "cli_test2", "1"]


def test_invalid_query(
    cli_runner: CliRunner,
    obj: Dict[str, Optional[str]],
) -> None:
    example_query = "select 'cli_test' as name 'cli_test2' as externalId"
    cli_result = cli_runner.invoke(query, [example_query], obj=obj)
    assert cli_result.exit_code == 1
    assert "Cognite API error has occurred" in cli_result.output
