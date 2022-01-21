-- insert datapoint from Signal Ocean Tonnage numeric timeseries, specifically for ETA
--  NOTES:
--    a. the target timeseries is INNER JOINED with already existing dataseries,
--       to prevent crashes from trying to insert a datapoint which does not exist
--       (externalId not found)
--    b. naming convention for timeseries: <IMO>:<etaPortId>:<variable_name>_signal_tonnage
--    c. input data fron AIS Exact Earth is limited to datapoints 
--       which are new, with respect to the last execution of the transformation
SELECT
  thedatapoint.externalId AS externalId,
  thedatapoint.value AS value,
  thedatapoint.timestamp AS timestamp
FROM
  (
    SELECT
      CONCAT (imo, ":", etaPortID, ":", thename) AS externalId,
      stack(
        1,
        "so_eta",
        --timestamp(eta),
        int(to_timestamp(STRING(eta), 'dd.MM.yyy HH:mm:ss')),
        "sec"
      ) AS (thename, value, uni),
    -- support compatibility with two different time formats
    if(
    isnotnull(  to_timestamp(string(date), 'dd.MM.yyyy HH:mm:ss') ),
      to_timestamp(string(date), 'dd.MM.yyyy HH:mm:ss'),
      to_timestamp(string(date), 'yyyy-MM-dd HH:mm:ss')
    )  AS timestamp
    FROM
      `src:002:signal:rawdb`.signal_tonnage_lists
    WHERE
      is_new("1.last_version_#2", lastUpdatedTime)
  ) AS thedatapoint
  INNER JOIN (
    SELECT
      externalId,
      id
    FROM
      _cdf.timeseries
  ) AS ts ON thedatapoint.externalId = ts.externalId
WHERE
  isnotnull(value)
  AND isnotnull(thedatapoint.externalId) --  AND  thedatapoint.externalId like "9203265%"
ORDER BY
  externalId