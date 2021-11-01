from typing import Dict, List, Optional

from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation

from cognite.transformations_cli.commands.list import list


def test_list(
    exp_client: ExpCogniteClient,
    obj: Dict[str, Optional[str]],
    test_transformation_ext_ids: List[str],
    configs_to_create: List[Transformation],
) -> None:
    # Create 4 transformations to make sure we have at least 4
    exp_client.transformations.create(configs_to_create)
    ctx = list.make_context("list", ["--limit=2"], obj=obj)
    with ctx:
        result = list.invoke(ctx)
        assert len(result) == 2
    ctx = list.make_context("list", ["--limit=4"], obj=obj)
    with ctx:
        result = list.invoke(ctx)
        assert len(result) == 4
    exp_client.transformations.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
