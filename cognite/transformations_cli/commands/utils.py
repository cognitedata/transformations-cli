import datetime
import sys
import textwrap
from typing import Callable, Iterator, List, Optional, TypeVar

import click
import sqlparse
from cognite.client import CogniteClient
from cognite.client.data_classes import (
    RawTable,
    Transformation,
    TransformationDestination,
    TransformationJob,
    TransformationJobMetric,
    TransformationNotification,
    TransformationPreviewResult,
)
from tabulate import tabulate


def get_transformation(client: CogniteClient, id: Optional[int], external_id: Optional[str]) -> Transformation:
    tr = client.transformations.retrieve(external_id=external_id, id=id)
    if tr:
        return tr
    msg = "external_id" if external_id else "id"
    sys.exit(
        f"Cognite API error has occurred: Transformation with {msg} {external_id if external_id else id} not found."
    )


def is_id_exclusive(id: Optional[int], external_id: Optional[str], should_exit: bool = True) -> bool:
    if id and external_id:
        if should_exit:
            sys.exit("Please only provide one of id and external id.")
        return False
    return True


def is_id_provided(id: Optional[int], external_id: Optional[str], should_exit: bool = True) -> bool:
    if not id and not external_id:
        if should_exit:
            sys.exit("Please provide one of id and external id.")
        return False
    return True


def exit_with_cognite_api_error(e: Exception) -> None:
    sys.exit(f"Cognite API error has occurred: {e}")
    return None  # To suppress mypy error


def get_table(destination: TransformationDestination) -> str:
    return destination.table if isinstance(destination, RawTable) else ""


def get_database(destination: TransformationDestination) -> str:
    return destination.database if isinstance(destination, RawTable) else ""


def print_transformations(transformation: List[Transformation]) -> str:
    # TODO print last_finished_job and running_job, schedule, blocked details when implemented in SDK
    list_columns = [["Name", "ID", "External ID", "Destination", "Database", "Table", "Data Set ID", "Action", "Tags"]]
    return tabulate(
        list_columns
        + [
            [
                t.name,
                t.id,
                t.external_id,
                t.destination.type,
                get_database(t.destination),
                get_table(t.destination),
                t.data_set_id,
                t.conflict_mode,
                ", ".join(t.tags) if t.tags else "",
            ]
            for t in transformation
        ],
        headers="firstrow",
        tablefmt="rst",
    )


def print_query(query: str, result: TransformationPreviewResult) -> str:
    print_res = f"Query:\n{print_sql(query)}\n"
    schema = result.schema
    results = result.results
    if schema:
        print_res += "\nSchema:\n"
        schema_content = [["name", "type", "nullable"]] + [
            [s.name, s.type.get("type", "") if isinstance(s.type, dict) else s.type.type, s.nullable] for s in schema
        ]
        print_res += tabulate(schema_content, headers="firstrow", tablefmt="rst") + "\n"
    if results:
        print_res += "\nResults:\n"
        res_content = [[key for key in results[0]]]
        for result in results:
            res_content.append(["\n".join(textwrap.wrap(str(result.get(key, "")))) for key in res_content[0]])
        print_res += tabulate(res_content, headers="firstrow", tablefmt="rst")
    return print_res


def print_sql(query: str) -> str:
    return sqlparse.format(query, reindent=True, keyword_case="upper")


def format_datetime(ms: Optional[int]) -> str:
    return str(datetime.datetime.fromtimestamp(ms / 1e3).replace(microsecond=0)) if ms else ""


def print_notifications(notifications: List[TransformationNotification]) -> bool:
    list_columns = [["ID", "Transformation ID", "Transformation External ID", "Destination", "Created Time"]]
    return tabulate(
        list_columns
        + [
            [n.id, n.transformation_id, n.transformation_external_id, n.destination, format_datetime(n.created_time)]
            for n in notifications
        ],
        headers="firstrow",
        tablefmt="rst",
    )


def print_metrics(metrics: List[TransformationJobMetric]) -> str:
    list_columns = [["Timestamp", "Metric Name", "Count"]]
    return tabulate(
        list_columns + [[format_datetime(m.timestamp), m.name, m.count] for m in metrics],
        headers="firstrow",
        tablefmt="rst",
    )


def get_job_duration(ms_start: Optional[int], ms_finished: Optional[int]) -> str:
    # TODO due to a bug in the backend, sometimes the finished_time is smaller than started_time. We use abs until fixed.
    return str(datetime.timedelta(milliseconds=abs(ms_finished - ms_start))) if ms_start and ms_finished else ""


def print_jobs(jobs: List[TransformationJob]) -> str:
    list_columns = [["ID", "Transformation ID", "Created Time", "Started Time", "Finished Time", "Duration", "Status"]]
    return tabulate(
        list_columns
        + [
            [
                j.id,
                j.transformation_id,
                format_datetime(j.created_time),
                format_datetime(j.started_time),
                format_datetime(j.finished_time),
                get_job_duration(j.started_time, j.finished_time),
                j.status,
            ]
            for j in jobs
        ],
        headers="firstrow",
        tablefmt="rst",
    )


T = TypeVar("T")


def chunk_items(items: List[T], n: int = 5) -> Iterator[List[T]]:
    for i in range(0, len(items), n):
        yield items[i : i + n]


def paginate(items: List[T], action: Callable[[List[T]], None]) -> None:
    for chunk in chunk_items(items):
        click.clear()
        action(chunk)
        input("Press Enter to continue")
