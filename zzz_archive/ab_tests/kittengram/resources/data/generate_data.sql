--Generate assignments

CREATE TEMP FUNCTION
  rand_DATE(min_date DATE,
    max_date DATE) AS ( TIMESTAMP_SECONDS( CAST( ROUND(UNIX_SECONDS(CAST(min_date AS TIMESTAMP)) + rand() * (UNIX_SECONDS(CAST(max_date AS TIMESTAMP)) - UNIX_SECONDS(CAST(min_date AS TIMESTAMP)))) AS INT64) ) );
CREATE TABLE
  `tmpsp1.ab.assignments_test` AS
SELECT
  GENERATE_UUID() AS userid,
  rand_DATE("2021-11-01",
    "2021-11-21") ts,
  CAST(ROUND(RAND()) AS INT64) AS groupid
FROM
  UNNEST(GENERATE_ARRAY(1, 60000));


--Generate activity table 
CREATE TABLE
  `tmpsp1.ab.activity_test` AS
WITH
  dates AS (
  SELECT
    GENERATE_DATE_ARRAY('2021-10-01', '2021-11-30') AS example),
  act1 AS (
  SELECT
    DISTINCT userid,
    dt,
    groupid,
    CASE
      WHEN CAST(ts AS date) = dt THEN CAST(ROUND(RAND()*10) AS INT64)
    ELSE
    CAST(ROUND(RAND()*20) AS INT64)
  END
    AS activity_level
  FROM
    `tmpsp1.ab.assignments_test`,
    dates,
    UNNEST(dates.example) AS dt )
SELECT
  userid,
  dt,
  groupid,
  CASE
    WHEN groupid = 0 and activity_level > 15 THEN 0
    WHEN groupid > 0 and dt < '2021-11-01' and activity_level > 15 THEN 0
    ELSE activity_level
END
  AS activity_level
FROM
  act1
ORDER BY
  dt;

---Second activity table 
CREATE TABLE
  `tmpsp1.ab.activity` AS
WITH
  dates AS (
  SELECT
    GENERATE_DATE_ARRAY('2021-10-01', '2021-11-30') AS example),
  act1 AS (
  SELECT
    DISTINCT userid,
    dt,
    groupid,
    CASE
      WHEN CAST(ts AS date) = dt THEN CAST(ROUND(RAND()*10) AS INT64)
    ELSE
    CAST(ROUND(RAND()*20) AS INT64)
  END
    AS activity_level
  FROM
    `tmpsp1.ab.assignments`,
    dates,
    UNNEST(dates.example) AS dt )
SELECT
  userid,
  dt,
  groupid,
  CASE
    WHEN groupid = 0 and activity_level > 10 THEN 0
    WHEN groupid > 0 and dt < '2021-11-01' and activity_level > 10 THEN 0
    ELSE CAST(ROUND(RAND()*20) AS INT64)
END
  AS activity_level
FROM
  act1
ORDER BY
  dt;


--Generate CTR table 
CREATE TABLE
  `tmpsp1.ab.ctr_test` AS
WITH
  active_users AS (
  SELECT
    userid,
    a.dt,
    groupid,
  FROM
    `tmpsp1.ab.activity_test` a
  INNER JOIN
    `tmpsp1.ab.assignments_test` b
  USING
    (userid)
  WHERE
    activity_level > 0)
SELECT
  userid,
  dt,
  groupid,
  CASE
    WHEN groupid = 0 THEN ROUND(RAND()*(35-25+1),2)+25
    WHEN groupid > 0
  AND dt <'2021-11-01' THEN ROUND(RAND()*(35-25+1),2)+25
  ELSE
  ROUND(RAND()*(45-35+1),2)+35
END
  AS ctr
FROM
  active_users;

--Second ctr table 
CREATE TABLE
  `tmpsp1.ab.ctr` AS
WITH
  active_users AS (
  SELECT
    userid,
    a.dt,
    groupid,
  FROM
    `tmpsp1.ab.activity` a
  INNER JOIN
    `tmpsp1.ab.assignments` b
  USING
    (userid, groupid)
  WHERE
    activity_level > 0)
SELECT
  userid,
  dt,
  groupid,
  CASE
    WHEN groupid = 0 THEN ROUND(RAND()*(35-30+1),2)+30
    WHEN groupid > 0
  AND dt <'2021-11-01' THEN ROUND(RAND()*(35-30+1),2)+30
  ELSE
  ROUND(RAND()*(40-35+1),2)+35
END
  AS ctr
FROM
  active_users