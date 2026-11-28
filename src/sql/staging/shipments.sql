
-- 1. Create the staging schema if it does not exist
CREATE SCHEMA IF NOT EXISTS staging;

-- 2. Rebuild the staging table
DROP TABLE IF EXISTS staging.shipments;

CREATE TABLE staging.shipments AS
WITH parsed AS (
    SELECT
        NULLIF(BTRIM(waybill_id), '') AS waybill_id,
        -- Dispatch timestamp supports both source formats:
        -- YYYY-MM-DD HH:MI:SS
        -- DD/MM/YYYY HH:MI
        CASE
            WHEN dispatch_timestamp ~ '^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$'
            THEN (
                SUBSTRING(dispatch_timestamp, 7, 4) || '-' ||
                SUBSTRING(dispatch_timestamp, 4, 2) || '-' ||
                SUBSTRING(dispatch_timestamp, 1, 2) ||
                SUBSTRING(dispatch_timestamp, 11)
            )::timestamp
            ELSE NULLIF(BTRIM(dispatch_timestamp), '')::timestamp
        END AS dispatch_timestamp,
        NULLIF(BTRIM(hub_arrival_timestamp), '')::timestamp
            AS hub_arrival_timestamp,
        NULLIF(BTRIM(hub_departure_timestamp), '')::timestamp
            AS hub_departure_timestamp,
        NULLIF(BTRIM(delivered_timestamp), '')::timestamp
            AS delivered_timestamp,
        BTRIM(cargo_weight_kg)::numeric AS cargo_weight_kg,
        BTRIM(freight_cost)::numeric AS freight_cost,
        UPPER(BTRIM(currency)) AS currency,
        BTRIM(shipment_status) AS shipment_status,
        BTRIM(corridor_code) AS corridor_code,
        BTRIM(corridor_type) AS corridor_type,
        BTRIM(origin_hub) AS origin_hub,
        BTRIM(destination_hub) AS destination_hub,
        BTRIM(distance_km)::numeric AS distance_km,
        BTRIM(sla_target_hours)::numeric AS sla_target_hours,
        BTRIM(vehicle_id) AS vehicle_id,
        BTRIM(fleet_ownership) AS fleet_ownership,
        BTRIM(vehicle_class) AS vehicle_class,
        NULLIF(BTRIM(carrier_partner_name), '') AS carrier_partner_name,
        _source,
        _loaded_at
    FROM raw.shipment_waybill_ledger
),
deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY waybill_id
            ORDER BY _loaded_at NULLS LAST
        ) AS row_num
    FROM parsed
),
unique_shipments AS (
    SELECT
        waybill_id,
        dispatch_timestamp,
        hub_arrival_timestamp,
        hub_departure_timestamp,
        delivered_timestamp,
        cargo_weight_kg,
        freight_cost,
        currency,
        shipment_status,
        corridor_code,
        corridor_type,
        origin_hub,
        destination_hub,
        distance_km,
        sla_target_hours,
        vehicle_id,
        fleet_ownership,
        vehicle_class,
        carrier_partner_name,
        _source,
        _loaded_at
    FROM deduplicated
    WHERE row_num = 1
),
metrics AS (
    SELECT
        *,
        EXTRACT(
            EPOCH FROM (delivered_timestamp - dispatch_timestamp)
        ) / 3600 AS actual_transit_hours,

        CASE
            WHEN hub_departure_timestamp >= hub_arrival_timestamp
            THEN EXTRACT(
                EPOCH FROM (
                    hub_departure_timestamp - hub_arrival_timestamp
                )
            ) / 3600
            ELSE NULL
        END AS hub_dwell_hours
    FROM unique_shipments
)
SELECT
    *,
    CASE
        WHEN actual_transit_hours IS NULL
          OR sla_target_hours IS NULL
        THEN NULL
        ELSE actual_transit_hours > sla_target_hours
    END AS sla_breached
FROM metrics;

-- enforce uniqueness at the database level:
ALTER TABLE staging.shipments
ADD CONSTRAINT shipments_pkey PRIMARY KEY (waybill_id);