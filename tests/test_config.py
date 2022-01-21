import os
from pathlib import Path

from cognite.transformations_cli.commands.deploy.transformation_config import parse_transformation_configs
from cognite.transformations_cli.commands.deploy.transformation_types import (
    ActionType,
    DestinationType,
    ReadWriteAuthentication,
    ScheduleConfig,
)


def rmdir(directory: Path) -> None:
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()


def write_config(test_name: str, contents: str, index: int) -> None:
    if index == 0 and os.path.isdir(test_name):
        rmdir(Path(test_name))
    if index == 0:
        os.mkdir(test_name)
    with open(f"{test_name}/trans_{index}.yml", "w") as f:
        f.write(contents)


def test_load_config_file_api_key() -> None:
    test_name = "test_load_config_file_api_key"
    file = """
externalId: testExternalId
name: testName
query: testQuery
authentication:
    read:
        apiKey: testApiKeyRead
    write:
        apiKey: testApiKeyWrite
schedule: testSchedule
destination:
    type: data_sets
    rawDatabase: testDb
    rawTable: testTable
notifications:
    - notif1
    - notif2
shared: true
ignoreNullFields: False
action: delete
"""
    write_config(test_name, file, 0)
    configs = parse_transformation_configs(test_name)
    conf = list(configs.values())[0]

    assert conf.external_id == "testExternalId"
    assert conf.name == "testName"
    assert conf.query == "testQuery"
    assert isinstance(conf.authentication, ReadWriteAuthentication)
    assert conf.authentication.read.api_key == "testApiKeyRead"
    assert conf.authentication.write.api_key == "testApiKeyWrite"
    assert conf.schedule == "testSchedule"
    assert conf.destination.type == DestinationType.data_sets
    assert conf.destination.raw_database == "testDb"
    assert conf.destination.raw_table == "testTable"
    assert len(conf.notifications) == 2
    assert conf.notifications[0] == "notif1"
    assert conf.notifications[1] == "notif2"
    assert conf.shared
    assert not conf.ignore_null_fields
    assert conf.action == ActionType.delete

    rmdir(Path(test_name))


def test_load_config_file_oidc() -> None:
    test_name = "test_load_config_file_oidc"
    file = """
externalId: testExternalId
name: testName
query:
    file: testQuery.sql
authentication:
    read:
        clientId: testClientIdRead
        clientSecret: testClientSecretRead
        tokenUrl: testTokenUrl
        scopes:
            - testScope1
            - testScope2
        cdfProjectName: testProject
        audience: testAudience
    write:
        clientId: testClientIdWrite
        clientSecret: testClientSecretWrite
        tokenUrl: testTokenUrl
        scopes:
            - testScope1
            - testScope2
        cdfProjectName: testProject
        audience: testAudience
schedule:
    interval: testSchedule
    isPaused: ${IS_PAUSED}
destination:
    type: string_datapoints
    rawDatabase: testDb
    rawTable: testTable
notifications:
    - notif1
    - notif2
shared: true
ignoreNullFields: False
action: delete
"""
    os.environ["IS_PAUSED"] = "false"
    write_config(test_name, file, 0)
    configs = parse_transformation_configs(test_name)
    conf = list(configs.values())[0]

    assert conf.external_id == "testExternalId"
    assert conf.name == "testName"
    assert conf.query.file == "testQuery.sql"
    assert isinstance(conf.authentication, ReadWriteAuthentication)

    assert conf.authentication.read.client_id == "testClientIdRead"
    assert conf.authentication.read.client_secret == "testClientSecretRead"
    assert conf.authentication.read.token_url == "testTokenUrl"
    assert len(conf.authentication.read.scopes) == 2
    assert conf.authentication.read.scopes[0] == "testScope1"
    assert conf.authentication.read.scopes[1] == "testScope2"
    assert conf.authentication.read.audience == "testAudience"

    assert conf.authentication.write.client_id == "testClientIdWrite"
    assert conf.authentication.write.client_secret == "testClientSecretWrite"
    assert conf.authentication.write.token_url == "testTokenUrl"
    assert len(conf.authentication.write.scopes) == 2
    assert conf.authentication.write.scopes[0] == "testScope1"
    assert conf.authentication.write.scopes[1] == "testScope2"
    assert conf.authentication.write.audience == "testAudience"

    assert conf.schedule == ScheduleConfig("testSchedule", False)
    assert conf.destination.type == DestinationType.string_datapoints
    assert conf.destination.raw_database == "testDb"
    assert conf.destination.raw_table == "testTable"
    assert len(conf.notifications) == 2
    assert conf.notifications[0] == "notif1"
    assert conf.notifications[1] == "notif2"
    assert conf.shared
    assert not conf.ignore_null_fields
    assert conf.action == ActionType.delete

    rmdir(Path(test_name))


def test_load_old_config_file_oidc() -> None:
    test_name = "test_load_old_config_file_oidc"
    file = """
legacy: true
externalId: testExternalId
name: testName
query: testQuery.sql
authentication:
    read:
        clientId: TEST_CLIENT_ID_READ
        clientSecret: TEST_CLIENT_SECRET_READ
        tokenUrl: testTokenUrl
        scopes:
            - testScope1
            - testScope2
        cdfProjectName: testProject
        audience: testAudience
    write:
        clientId: TEST_CLIENT_ID_WRITE
        clientSecret: TEST_CLIENT_SECRET_WRITE
        tokenUrl: testTokenUrl
        scopes:
            - testScope1
            - testScope2
        cdfProjectName: testProject
        audience: testAudience
schedule: testSchedule
destination:
    type: stringDatapoints
    rawDatabase: testDb
    rawTable: testTable
notifications:
    - notif1
    - notif2
shared: true
ignoreNullFields: False
action: Delete
"""
    write_config(test_name, file, 0)

    os.environ["TEST_CLIENT_ID_READ"] = "testClientIdRead"
    os.environ["TEST_CLIENT_ID_WRITE"] = "testClientIdWrite"
    os.environ["TEST_CLIENT_SECRET_READ"] = "testClientSecretRead"
    os.environ["TEST_CLIENT_SECRET_WRITE"] = "testClientSecretWrite"

    configs = parse_transformation_configs(test_name)
    conf = list(configs.values())[0]

    assert conf.external_id == "testExternalId"
    assert conf.name == "testName"
    assert conf.query.file == "testQuery.sql"
    assert isinstance(conf.authentication, ReadWriteAuthentication)

    assert conf.authentication.read.client_id == "testClientIdRead"
    assert conf.authentication.read.client_secret == "testClientSecretRead"
    assert conf.authentication.read.token_url == "testTokenUrl"
    assert len(conf.authentication.read.scopes) == 2
    assert conf.authentication.read.scopes[0] == "testScope1"
    assert conf.authentication.read.scopes[1] == "testScope2"
    assert conf.authentication.read.audience == "testAudience"

    assert conf.authentication.write.client_id == "testClientIdWrite"
    assert conf.authentication.write.client_secret == "testClientSecretWrite"
    assert conf.authentication.write.token_url == "testTokenUrl"
    assert len(conf.authentication.write.scopes) == 2
    assert conf.authentication.write.scopes[0] == "testScope1"
    assert conf.authentication.write.scopes[1] == "testScope2"
    assert conf.authentication.write.audience == "testAudience"

    assert conf.schedule == "testSchedule"
    assert conf.destination.type == DestinationType.string_datapoints
    assert conf.destination.raw_database == "testDb"
    assert conf.destination.raw_table == "testTable"
    assert len(conf.notifications) == 2
    assert conf.notifications[0] == "notif1"
    assert conf.notifications[1] == "notif2"
    assert conf.shared
    assert not conf.ignore_null_fields
    assert conf.action == ActionType.delete

    rmdir(Path(test_name))


def test_load_old_config_file_api_key() -> None:
    test_name = "test_load_old_config_file_api_key"
    file = """
externalId: testExternalId
name: testName
query: testQuery.sql
apiKey:
    read: TEST_API_KEY_READ
    write: TEST_API_KEY_WRITE
schedule: testSchedule
legacy: true
destination:
    type: dataSets
    rawDatabase: testDb
    rawTable: testTable
notifications:
    - notif1
    - notif2
shared: true
ignoreNullFields: False
action: DELETE
"""
    write_config(test_name, file, 0)
    os.environ["TEST_API_KEY_READ"] = "testApiKeyRead"
    os.environ["TEST_API_KEY_WRITE"] = "testApiKeyWrite"

    configs = parse_transformation_configs(test_name)
    conf = list(configs.values())[0]

    assert conf.external_id == "testExternalId"
    assert conf.name == "testName"
    assert conf.query.file == "testQuery.sql"
    assert isinstance(conf.authentication, ReadWriteAuthentication)
    assert conf.authentication.read.api_key == "testApiKeyRead"
    assert conf.authentication.write.api_key == "testApiKeyWrite"
    assert conf.schedule == "testSchedule"
    assert conf.destination.type == DestinationType.data_sets
    assert conf.destination.raw_database == "testDb"
    assert conf.destination.raw_table == "testTable"
    assert len(conf.notifications) == 2
    assert conf.notifications[0] == "notif1"
    assert conf.notifications[1] == "notif2"
    assert conf.shared
    assert not conf.ignore_null_fields
    assert conf.action == ActionType.delete

    rmdir(Path(test_name))


def test_validate_destination_type() -> None:
    pass


def test_validate_exclusive_auth() -> None:
    pass


def test_validate_auth() -> None:
    pass


def test_validate_config() -> None:
    pass


def test_parse_transformation_config() -> None:
    pass


def test_parse_transformation_configs() -> None:
    pass


def test_to_transformation() -> None:
    pass


def test_to_action() -> None:
    pass


def test_to_destination() -> None:
    pass


def test_to_query() -> None:
    pass


def test_to_read_api_key() -> None:
    pass


def test_to_write_api_key() -> None:
    pass


def test_stringify_scopes() -> None:
    pass


def test_get_default_scopes() -> str:
    pass


def test_is_oidc_defined() -> None:
    pass


def test_get_oidc() -> None:
    pass


def test_to_read_oidc() -> None:
    pass


def test_to_write_oidc() -> None:
    pass


def test_to_schedule() -> None:
    pass


def test_to_notification() -> None:
    pass


def test_get_existing_transformation_ext_ids() -> None:
    pass


def test_get_new_transformation_ids() -> None:
    pass
