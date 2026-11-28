-- staging.maintenance
SET ROLE fleet_writer;

BEGIN;

DROP TABLE IF EXISTS staging.maintenance;

CREATE TABLE staging.maintenance AS
SELECT
    btrim(maintenance_id)                          AS maintenance_id,
    btrim(vehicle_id)                              AS vehicle_id,
    CASE left(btrim(vehicle_id), 4)
        WHEN 'VEH-' THEN 'VEH'
        WHEN 'TRK_' THEN 'TRK'
        ELSE 'OTHER'
    END                                            AS vehicle_id_format,
    btrim(incident_timestamp)::timestamp           AS incident_timestamp,
    btrim(incident_timestamp)::timestamp::date     AS incident_date,
    btrim(downtime_hours)::numeric(6,1)            AS downtime_hours,
    btrim(repair_cost_usd)::numeric(10,2)          AS repair_cost_usd,
    btrim(failure_category)                        AS failure_category,
    (btrim(downtime_hours)::numeric = 0)           AS flag_zero_downtime,
    _source,
    _loaded_at
FROM raw.fleet_maintenance_audit;

ALTER TABLE staging.maintenance ADD PRIMARY KEY (maintenance_id);
CREATE INDEX idx_staging_maintenance_vehicle  ON staging.maintenance (vehicle_id);
CREATE INDEX idx_staging_maintenance_incident ON staging.maintenance (incident_date);

COMMENT ON TABLE staging.maintenance IS
    'Cleaned fleet maintenance events. One row per maintenance_id. Source: raw.fleet_maintenance_audit. repair_cost_usd is in USD.';

COMMIT;

ANALYZE staging.maintenance;

-- Back to your own login for the read-only checks below
RESET ROLE;

-- ---------------------------------------------------------------------
-- Validation checks: every row should say PASS
-- ---------------------------------------------------------------------
SELECT check_name, actual, expected,
       CASE WHEN actual = expected THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT 'row count matches raw' AS check_name,
           (SELECT COUNT(*) FROM staging.maintenance)::text AS actual,
           (SELECT COUNT(*) FROM raw.fleet_maintenance_audit)::text AS expected
    UNION ALL
    SELECT 'maintenance_id is unique',
           (SELECT COUNT(DISTINCT maintenance_id) FROM staging.maintenance)::text,
           (SELECT COUNT(*) FROM staging.maintenance)::text
    UNION ALL
    SELECT 'no NULLs in typed columns',
           (SELECT COUNT(*) FROM staging.maintenance
             WHERE incident_timestamp IS NULL OR downtime_hours IS NULL OR repair_cost_usd IS NULL)::text,
           '0'
    UNION ALL
    SELECT 'downtime hours total unchanged by casting',
           (SELECT SUM(downtime_hours) FROM staging.maintenance)::text,
           (SELECT SUM(downtime_hours::numeric) FROM raw.fleet_maintenance_audit)::text
    UNION ALL
    SELECT 'repair cost total unchanged by casting',
           (SELECT SUM(repair_cost_usd) FROM staging.maintenance)::text,
           (SELECT SUM(repair_cost_usd::numeric) FROM raw.fleet_maintenance_audit)::text
    UNION ALL
    SELECT 'five failure categories',
           (SELECT COUNT(DISTINCT failure_category) FROM staging.maintenance)::text,
           '5'
    UNION ALL
    SELECT 'vehicle_ids missing from waybill ledger',
           (SELECT COUNT(*) FROM staging.maintenance m
             WHERE NOT EXISTS (SELECT 1 FROM raw.shipment_waybill_ledger w
                               WHERE w.vehicle_id = m.vehicle_id))::text,
           '0'
) checks;
