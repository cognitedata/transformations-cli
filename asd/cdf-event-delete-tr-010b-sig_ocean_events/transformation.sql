SELECT
    --externalId,
    id
FROM
    _cdf.events
WHERE
    dataSetId = dataset_id("src:002:signal")
    AND source = 'signal_ocean'
    AND type = 'SO Voyage Event'