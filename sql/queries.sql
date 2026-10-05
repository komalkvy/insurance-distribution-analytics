-- Each query starts with a "-- name:" line. The Python script runs them all
-- against the SQLite table `leads` and saves each result to outputs/sql_<name>.csv

-- name: overall
SELECT COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct,
       ROUND(AVG(annual_premium)) AS avg_premium
FROM leads;

-- name: by_age_band
SELECT age_band,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct,
       ROUND(AVG(annual_premium)) AS avg_premium
FROM leads
GROUP BY age_band
ORDER BY age_band;

-- name: by_previously_insured
SELECT previously_insured,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct
FROM leads
GROUP BY previously_insured;

-- name: by_vehicle_damage
SELECT vehicle_damage,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct
FROM leads
GROUP BY vehicle_damage;

-- name: by_vehicle_age
SELECT vehicle_age,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct
FROM leads
GROUP BY vehicle_age;

-- name: by_gender
SELECT gender,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct
FROM leads
GROUP BY gender;

-- name: by_customer_type
SELECT previously_insured,
       vehicle_damage,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct
FROM leads
GROUP BY previously_insured, vehicle_damage
ORDER BY conv_pct DESC;

-- name: by_region
SELECT region_code,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct,
       ROUND(AVG(annual_premium)) AS avg_premium
FROM leads
GROUP BY region_code
ORDER BY leads DESC;

-- name: by_channel
SELECT policy_sales_channel AS channel,
       COUNT(*) AS leads,
       SUM(response) AS conversions,
       ROUND(100.0 * SUM(response) / COUNT(*), 2) AS conv_pct,
       ROUND(AVG(annual_premium)) AS avg_premium
FROM leads
GROUP BY policy_sales_channel
ORDER BY leads DESC;
