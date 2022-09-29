import uuid
from typing import Dict, List, Optional

from click.testing import CliRunner
from cognite.client import CogniteClient
from cognite.client.data_classes import DataSet, Transformation, TransformationDestination

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


def test_list_data_set_id(
    client: CogniteClient, obj: Dict[str, Optional[str]], cli_runner: CliRunner, new_dataset: DataSet
) -> None:
    uui_str = uuid.uuid1()
    ext_id1 = f"CLI_FILTER_TEST_{uui_str}"
    ext_id2 = f"CLI_FILTER_TEST_1_{uui_str}"

    client.transformations.create(
        [
            Transformation(
                external_id=ext_id1,
                name=ext_id1,
                destination=TransformationDestination.assets(),
                conflict_mode="upsert",
                query="select 'asd' as name, 'asd' as externalId",
                is_public=True,
                data_set_id=new_dataset.id,
            ),
            Transformation(
                external_id=ext_id2,
                name=ext_id2,
                destination=TransformationDestination.assets(),
                conflict_mode="upsert",
                query="select 'asd' as name, 'asd' as externalId",
                is_public=True,
            ),
        ]
    )
    result = cli_runner.invoke(list, [f"--data-set-id={new_dataset.id}", "--limit=1000"], obj=obj)
    client.transformations.delete(external_id=[ext_id1, ext_id2])
    assert result.exit_code == 0
    assert ext_id2 not in result.output
    assert ext_id1 in result.output


def test_list_tags(client: CogniteClient, obj: Dict[str, Optional[str]], cli_runner: CliRunner) -> None:
    uui_str = uuid.uuid1()
    ext_id1 = f"CLI_FILTER_TEST_{uui_str}"
    ext_id2 = f"CLI_FILTER_TEST_1_{uui_str}"
    ext_id3 = f"CLI_FILTER_TEST_2_{uui_str}"

    import time

    tag_postfix = time.time()
    hai_tag = f"hai_{tag_postfix}"
    vu_tag = f"vu_{tag_postfix}"
    nguyen_tag = f"nguyen_{tag_postfix}"

    client.transformations.create(
        [
            Transformation(
                external_id=ext_id1,
                name=ext_id1,
                destination=TransformationDestination.assets(),
                conflict_mode="upsert",
                query="select 'asd' as name, 'asd' as externalId",
                is_public=True,
                tags=[hai_tag, vu_tag],
            ),
            Transformation(
                external_id=ext_id2,
                name=ext_id2,
                destination=TransformationDestination.assets(),
                conflict_mode="upsert",
                query="select 'asd' as name, 'asd' as externalId",
                is_public=True,
                tags=[vu_tag, nguyen_tag],
            ),
            Transformation(
                external_id=ext_id3,
                name=ext_id2,
                destination=TransformationDestination.assets(),
                conflict_mode="upsert",
                query="select 'asd' as name, 'asd' as externalId",
                is_public=True,
            ),
        ]
    )
    result = cli_runner.invoke(list, [f"--tag={vu_tag}", "--limit=1000"], obj=obj)
    result2 = cli_runner.invoke(list, [f"--tag={hai_tag}", "--limit=1000"], obj=obj)
    result3 = cli_runner.invoke(list, [f"--tag={nguyen_tag}", "--limit=1000"], obj=obj)
    client.transformations.delete(external_id=[ext_id1, ext_id2, ext_id3])

    assert result.exit_code == 0
    assert ext_id3 not in result.output
    assert ext_id2 in result.output
    assert ext_id1 in result.output
    assert hai_tag in result.output and vu_tag in result.output

    assert result2.exit_code == 0
    assert ext_id3 not in result2.output
    assert ext_id2 not in result2.output
    assert ext_id1 in result2.output
    assert hai_tag in result2.output and vu_tag in result2.output

    assert result3.exit_code == 0
    assert ext_id3 not in result3.output
    assert ext_id1 not in result3.output
    assert ext_id2 in result3.output
    assert hai_tag not in result3.output and vu_tag in result3.output and nguyen_tag in result3.output
