-- process Signal Ocean Voyage data and create CDF Events
-- the IMO value of the Voyage is used to set
-- the assetIds  to the Vessel asset identified by the IMO
-- externalID of the voyage Event set to CONCAT(IMO,':',id)
--    this means externalID is made unique by including ID
-- assetId set the vessel with the IMO number which reported in the Voyage
SELECT
    CONCAT(IMO, ':', voyages.ID) AS externalId,
    dataset_id('src:002:signal') AS dataSetId,
    array(bigint(vessels.id)) AS assetIds,
    'signal_ocean' AS source,
    timestamp(StartDate) AS startTime,
    --timestamp(EndDate) AS endTime,
    'SO Voyage' AS type,
    -- to be confirmed
    Horizon AS subtype,
    --will soon be deployed from GH
    CASE
        WHEN timestamp(EndDate) < add_months(timestamp(StartDate), 60) THEN timestamp(EndDate)
        ELSE NULL
    END AS endTime,
    CONCAT(
        'Signal Ocean voyage with number ',
        VoyageNumber,
        ' and id ',
        id,
        ', for the vessel ',
        IMO,
        ' (IMO)'
    ) AS description,
    to_metadata(
        ID,
        Horizon,
        VesselName,
        VesselTypeID,
        VesselType,
        VesselClassID,
        VesselClass,
        TradeID,
        Trade,
        VesselStatusID,
        VesselStatus,
        CommercialOperatorID,
        CommercialOperator,
        CargoTypeID,
        CargoType,
        CargoGroupID,
        CargoGroup,
        CargoTypeSource,
        BallastDistance
    ) AS metadata
FROM
    (
        SELECT
            RANK() OVER(
                PARTITION BY IMO,
                VoyageNumber
                ORDER BY
                    lastUpdatedTime DESC
            ) Rank,
            *
        FROM
            `src:002:signal:rawdb`.signal_voyages
        WHERE
        WHERE
            is_new("1.last_version_#5", lastUpdatedTime)
    ) AS voyages -- join with existing Vessels to makes sure the parentage is safe/possible
    INNER JOIN (
        SELECT
            externalId,
            id
        FROM
            _cdf.assets
        WHERE
            parentExternalId = "Vessels"
    ) AS vessels ON voyages.IMO = vessels.externalId
WHERE
    Rank = 1
