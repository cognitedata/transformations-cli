from enum import Enum


class DestinationType(Enum):
    assets = "assets"
    timeseries = "timeseries"
    assethierarchy = "assethierarchy"
    events = "events"
    datapoints = "datapoints"
    stringdatapoints = "stringdatapoints"
    sequences = "sequences"
    files = "files"
    labels = "labels"
    relationships = "relationships"
    raw = "raw"
    raw_table = "raw_table"


class ActionType(Enum):
    create = "abort"
    abort = "abort"
    update = "update"
    upsert = "upsert"
    delete = "delete"
