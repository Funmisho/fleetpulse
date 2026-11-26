import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from load_utils import replace_raw_table

load_dotenv()
DB_PATH = Path(os.getenv("DATA_DIR", "data/raw")) / "logistics_core.db"

# source table -> raw table (drops the redundant "raw_" prefix)
TABLES = {
    "raw_shipment_waybill_ledger": "shipment_waybill_ledger",
    "fleet_maintenance_audit": "fleet_maintenance_audit",
}


def main():
    src = sqlite3.connect(DB_PATH)
    try:
        for source_table, target in TABLES.items():
            expected = src.execute(f'SELECT COUNT(*) FROM "{source_table}"').fetchone()[0]
            cur = src.execute(f'SELECT * FROM "{source_table}"')
            columns = [d[0] for d in cur.description]
            print(f"Loading {source_table} -> raw.{target} ({expected:,} rows)")
            n = replace_raw_table(target, columns, cur, source=f"logistics_core.db:{source_table}")
            status = "OK" if n == expected else "MISMATCH"
            print(f"  {status}: sent {n:,} of {expected:,}\n")
    finally:
        src.close()


if __name__ == "__main__":
    main()