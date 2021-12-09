-- Create string timeseries parsing TONNAGE api data (all string/date except ETA)
-- UPDATE BELOW when YOU'RE DONE
--  NOTES:
--    a. naming convention for timeseries:<IMO>:<variable_name>_signal_tonnage
--    b. timeseries to be created are INNER JOINED with Vessels already existing
--       to prefound externalId
--    c. input data fronSignal Ocean signal_tonnage_lists 
--       is restricted to datapoints new, 
--       with respect to the last execution of the transformation
SELECT
  externalId,
  externalId AS name,
  assetId,
  unit,
  to_metadata(ts_type, source_type) AS metadata,
  dataset_id("src:002:signal") AS dataSetId,
  TRUE AS isString,
  CONCAT(
    "Signal Ocean Tonnage vesselIMO:variable_name ",
    oneimo,
    ":",
    thename
  ) AS description
FROM
  (
    SELECT
      RANK() OVER(
        PARTITION BY exact_vessels.externalId
        ORDER BY
          exact_vessels.lastUpdatedTime DESC
      ) Rank,
      *
    FROM
      (
        SELECT
          CONCAT (imo, ":", thename) AS externalId,
          imo AS oneimo,
          etaPortID AS etaPortID,
          uni AS unit,
          "sourceSOton" AS ts_type,
          "signal ocean tonnage" AS source_type,
          stack(
            13,
            -- openAreas -- ignore for now
            "latestAis",
            STRING(latestAis),
            "sec",
            "availabilityDateType",
            STRING(availabilityDateType),
            "-",
            "pushType",
            STRING(pushType),
            "-",
            "availabilityPortType",
            STRING(availabilityPortType),
            "-",
            "commercialOperator",
            STRING(commercialOperator),
            "-",
            "fixtureType",
            STRING(fixtureType),
            "-",
            "operationalStatus",
            STRING(operationalStatus),
            "-",
            "commercialStatus",
            STRING(commercialStatus),
            "-",
            "date",
            STRING(date),
            "sec",
            "marketDeployment",
            STRING(marketDeployment),
            "-",
            "openPredictionAccuracy",
            STRING(openPredictionAccuracy),
            "-",
            "openDate",
            STRING(openDate),
            "sec",
            "openPort",
            STRING(openPort),
            "-"
          ) AS (thename, value, uni),
          vessels.id AS assetId,
          so_tonnage.lastUpdatedTime AS lastUpdatedTime,
          vessels.externalId AS theimo
        FROM
          (
            SELECT
              *
            FROM
              `src:002:signal:rawdb`.signal_tonnage_lists
            WHERE
              is_new(
                "1.last_version_#1",
                lastUpdatedTime
              )
          ) AS so_tonnage
          INNER JOIN (
            SELECT
              externalId,
              id
            FROM
              _cdf.assets
            WHERE
              parentExternalId = "Vessels"
          ) AS vessels ON so_tonnage.imo = vessels.externalId
      ) AS exact_vessels
  ) AS ranked_exact_vessels
WHERE
  Rank = 1 --  AND  externalId like "9203265%" -- TODO can go away after DEVELOPMENT
ORDER BY
  externalId -- TODO can go away after DEVELOPMENT