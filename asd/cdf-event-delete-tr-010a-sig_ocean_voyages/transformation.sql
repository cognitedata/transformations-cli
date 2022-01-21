SELECT
    -- xternalId,
    id
FROM
    _cdf.events
WHERE
    dataSetId = dataset_id("src:002:signal") -- AND externalId LIKE "voyage:%"
    AND source = 'signal_ocean'
    AND type = 'SO Voyage'