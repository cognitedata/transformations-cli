-- create Events for each entry of the table event
-- the IMO in the Event is used to set the assetIds  to the Vessel asset
-- identified by the IMO
SELECT
    CONCAT(
        voyages.IMO_voyages,
        ':',
        voyages.id_voyages,
        ":",
        ID
    ) AS externalId,
    array(vessels.id) AS assetIds,
    dataset_id('src:002:signal') AS dataSetId,
    CONCAT(
        'Signal Ocean Event with id ',
        sig_events.ID,
        ' for voyage ',
        VoyageID,
        ' of the vessel ',
        voyages.IMO_voyages,
        ' (IMO)'
    ) AS description,
    'SO Voyage Event' AS type,
    CONCAT(EventType, ':', Purpose) AS subtype,
    if(
        to_timestamp(EventDate, 'dd.MM.yyyy HH:mm:ss') > make_timestamp(1970, 1, 1, 0, 0, 0),
        to_timestamp(EventDate, 'dd.MM.yyyy HH:mm:ss'),
        to_timestamp(ArrivalDate, 'dd.MM.yyyy HH:mm:ss')
    ) AS startTime,
    ifnull(to_timestamp(SailingDate, 'dd.MM.yyyy HH:mm:ss'), NULL)AS endTime,
    -- Only Voyage:Start has an EventDate, which is equivalent to the startTime
    -- EventDate is not shown as null, but as 0001-01-01 00:00:00, therefore the sanity check
    'signal_ocean' AS source,
    to_metadata(
        ID,
        EventType,
        Purpose,
        VoyageID,
        EventHorizon,
        EventDate,
        ArrivalDate,
        SailingDate,
        Latitude,
        Longitude,
        GeoAssetID,
        GeoAssetName,
        PortID,
        PortName
    ) AS metadata
FROM
    (
        SELECT
            *
        FROM
            `src:002:signal:rawdb`.signal_events -- WHERE TRUE
        WHERE
            is_new("1.last_version_#7", lastUpdatedTime)
    ) AS sig_events -- join the events to the voyages to ensure
    -- we publish only events which are parts of a voyage
    -- if not, we can't really know which IMO/Vessel to attach the event to
    -- furthermore, this join also gives us the IMO of the vessel
    INNER JOIN (
        SELECT
            bigint(split(externalId, ':') [0]) AS IMO_voyages,
            STRING(split(externalId, ':') [1]) AS id_voyages,
            externalId,
            id
        FROM
            _cdf.events
        WHERE
            dataSetId = dataset_id("src:002:signal")
            AND source = 'signal_ocean'
            AND type = 'SO Voyage'
    ) AS voyages ON voyages.id_voyages = sig_events.VoyageID -- join the voyages to the Vessels
    -- in ordert to get the CDF id corresponding to the IMO included in the voyage
    -- such id is necessary to set assetIds
    INNER JOIN (
        SELECT
            externalId,
            id
        FROM
            _cdf.assets
        WHERE
            parentExternalId = "Vessels"
    ) AS vessels ON voyages.IMO_voyages = vessels.externalId
