# fleetpulse
Operational intelligence platform for logistics SLA monitoring, fleet efficiency and predictive dispatch decision-making.

## Setup

1. `python3 -m venv .venv` and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your own database login
4. Put the source files in `data/raw/` (see `docs/DATASET.md`)
5. Test your connection: `python src/check_connection.py`

## Loading raw data

```
python src/load_sqlite.py   # raw.shipment_waybill_ledger, raw.fleet_maintenance_audit
```