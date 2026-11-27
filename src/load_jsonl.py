import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from load_utils import replace_raw_table

load_dotenv()
DATA = Path(os.getenv("DATA_DIR", "data/raw"))
FILE = DATA / "gps_telemetry_events.jsonl"
TABLE = "gps_telemetry_events"
COLUMNS = ["event_id", "waybill_id", "event_type", "tz_offset", "metadata"]


def count_events(path):
    """Independent pass over the file, used to check the load."""
    with open(path, encoding="utf-8-sig") as fh:
        return sum(1 for line in fh if line.strip())


def iter_rows(path, stats):
    with open(path, encoding="utf-8-sig") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path.name} line {line_no}: invalid JSON ({e})") from e

            # a new field in the file should stop the load, not be silently dropped
            unexpected = set(rec) - set(COLUMNS)
            if unexpected:
                raise ValueError(f"{path.name} line {line_no}: unexpected keys {sorted(unexpected)}")

            metadata = rec.get("metadata")
            if metadata is None:
                stats["no_metadata"] += 1
                metadata_json = None
            else:
                metadata_json = json.dumps(metadata)

            yield (
                rec.get("event_id"),
                rec.get("waybill_id"),
                rec.get("event_type"),
                rec.get("tz_offset"),
                metadata_json,
            )


def main():
    if not FILE.exists():
        sys.exit(f"{FILE} not found. Put the file in {DATA} (or set DATA_DIR in .env).")

    expected = count_events(FILE)
    stats = {"no_metadata": 0}
    print(f"Loading {FILE.name} -> raw.{TABLE} ({expected:,} events)")
    n = replace_raw_table(
        TABLE,
        COLUMNS,
        iter_rows(FILE, stats),
        source=FILE.name,
        column_types={"metadata": "JSONB"},
    )
    status = "OK" if n == expected else "MISMATCH"
    print(f"  {status}: sent {n:,} of {expected:,}")
    print(f"  events with no metadata (stored as NULL): {stats['no_metadata']:,} ({stats['no_metadata'] / max(n, 1):.1%})\n")

    if n != expected:
        sys.exit("Row count does not match the file. Fix the cause and run again (loads are replace-style, so re-running is safe).")


if __name__ == "__main__":
    main()
