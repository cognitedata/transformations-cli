from typing import Dict, List, Optional

from click.testing import CliRunner
from cognite.client import CogniteClient
from cognite.client.data_classes import Transformation

from cognite.transformations_cli.commands.list import list
from tests.helpers import from_table


def test_list(
    client: CogniteClient,
    obj: Dict[str, Optional[str]],
    cli_runner: CliRunner,
    test_transformation_ext_ids: List[str],
    configs_to_create: List[Transformation],
) -> None:
    # Create 4 transformations to make sure we have at least 4
    client.transformations.create(configs_to_create)
    result = cli_runner.invoke(list, ["--limit=2"], obj=obj)
    assert result.exit_code == 0
    res_limit2 = from_table(result.output)
    assert len(res_limit2) == 3  # with header, 3 rows

    result = cli_runner.invoke(list, ["--limit=4"], obj=obj)
    assert result.exit_code == 0
    res_limit4 = from_table(result.output)
    assert len(res_limit4) == 5  # with header, 5 rows
    client.transformations.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
