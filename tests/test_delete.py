from typing import List

import pytest
from cognite.experimental import CogniteClient as ExpCogniteClient
from cognite.experimental.data_classes.transformations import Transformation


@pytest.mark.unit
def test_delete(
    exp_client: ExpCogniteClient,
    test_transformation_ext_ids: List[str],
    configs_to_create: List[Transformation],
) -> None:
    # Clean up before the test
    exp_client.transformations.schedules.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
    exp_client.transformations.delete(external_id=test_transformation_ext_ids, ignore_unknown_ids=True)
    assert True
