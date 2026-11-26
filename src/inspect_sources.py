import json
import os
import sqlite3
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
DATA = Path(os.getenv("DATA_DIR", "data/raw"))

print("=== SQLite: logistics_core.db ===")
con = sqlite3.connect(DATA / "logistics_core.db")
tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
for t in tables:
    n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    cols = [c[1] for c in con.execute(f'PRAGMA table_info("{t}")')]
    print(f"\n{t}: {n:,} rows, {len(cols)} columns")
    print("  ", cols)
pages, page_size, free = (con.execute(f"PRAGMA {p}").fetchone()[0]
                          for p in ("page_count", "page_size", "freelist_count"))
print(f"\nfile pages: {pages:,}  free pages: {free:,}  page size: {page_size}")
con.close()

print("\n=== CSVs (first 3 raw lines each) ===")
for f in sorted((DATA / "legacy_carrier_and_fuel_logs").glob("*.csv")):
    with open(f, encoding="utf-8", errors="replace") as fh:
        lines = [next(fh, "").rstrip("\n") for _ in range(3)]
        total = 3 + sum(1 for _ in fh)
    print(f"\n{f.name}: ~{total - 1:,} data rows")
    for line in lines:
        print("  ", line[:200])

print("\n=== JSONL: gps_telemetry_events.jsonl ===")
keys, meta_keys, events, bad, n = Counter(), Counter(), Counter(), 0, 0
with open(DATA / "gps_telemetry_events.jsonl", encoding="utf-8", errors="replace") as fh:
    for i, line in enumerate(fh):
        n += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        keys.update(rec.keys())
        events[rec.get("event_type")] += 1
        if isinstance(rec.get("metadata"), dict):
            meta_keys.update(rec["metadata"].keys())
        if i < 2:
            print("  sample:", json.dumps(rec)[:300])
print(f"\nlines: {n:,}  unparseable: {bad:,}")
print("top-level keys:", dict(keys))
print("metadata keys :", dict(meta_keys))
print("event types   :", dict(events))