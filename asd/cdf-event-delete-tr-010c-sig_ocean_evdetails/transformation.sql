SELECT
    --externalId,
    id
FROM
    _cdf.events
WHERE
    dataSetId = dataset_id("src:002:signal") --AND externalId LIKE "so_evd:%" --AND externalId LIKE "so_evd:%"
    AND source = 'signal_ocean'
    AND type = 'SO Voyage Event Detail'