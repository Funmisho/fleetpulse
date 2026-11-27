"""Loads the three legacy CSV extracts into the raw schema.

"""
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from load_utils import replace_raw_table

load_dotenv()
DATA = Path(os.getenv("DATA_DIR", "data/raw"))

# file name -> (raw table, delimiter, expected header)
# The header is checked so a changed file fails loudly instead of loading wrongly.
# Note the fuel file: delimiter is ";" and its column order differs from the data dictionary.
SOURCES = {
    "third_party_partner_invoices.csv": (
        "third_party_partner_invoices",
        ",",
        ["invoice_ref", "waybill_ref", "partner_name", "billed_amount_local",
         "curr", "detention_surcharge", "invoice_status"],
    ),
    "fuel_card_dispense_logs.csv": (
        "fuel_card_dispense_logs",
        ";",
        ["tx_ref", "truck_reg", "swipe_timestamp", "liters_dispensed",
         "unit_price_local", "currency_code", "station_hub"],
    ),
    "border_customs_clearance.csv": (
        "border_customs_clearance",
        ",",
        ["clearance_id", "shipment_ref", "border_post", "hold_hours", "duty_status"],
    ),
}


def find_file(name):
    """The data dictionary puts the CSVs in legacy_carrier_and_fuel_logs/;
    a flat data/raw/ layout works too."""
    for folder in (DATA / "legacy_carrier_and_fuel_logs", DATA):
        path = folder / name
        if path.exists():
            return path
    raise FileNotFoundError(f"{name} not found under {DATA} or {DATA / 'legacy_carrier_and_fuel_logs'}")


def open_csv(path, delimiter):
    # utf-8-sig drops a byte-order mark if one is present; newline="" is what the csv module expects
    fh = open(path, encoding="utf-8-sig", newline="")
    return fh, csv.reader(fh, delimiter=delimiter)


def count_data_rows(path, delimiter):
    """Independent pass over the file, used to check the load."""
    fh, reader = open_csv(path, delimiter)
    with fh:
        next(reader)  # header
        return sum(1 for _ in reader)


def iter_rows(path, delimiter, width):
    fh, reader = open_csv(path, delimiter)
    with fh:
        next(reader)  # header
        for line_no, row in enumerate(reader, start=2):
            if len(row) != width:
                raise ValueError(f"{path.name} line {line_no}: expected {width} fields, got {len(row)}")
            yield row  # empty cells stay as empty strings; staging decides what they mean


def main():
    failed = False
    for file_name, (table, delimiter, expected_header) in SOURCES.items():
        path = find_file(file_name)

        fh, reader = open_csv(path, delimiter)
        with fh:
            header = next(reader)
        if header != expected_header:
            sys.exit(f"{file_name}: header does not match.\n  expected {expected_header}\n  found    {header}")

        expected = count_data_rows(path, delimiter)
        print(f"Loading {path.name} -> raw.{table} ({expected:,} rows)")
        n = replace_raw_table(
            table,
            header,
            iter_rows(path, delimiter, len(header)),
            source=path.name,
        )
        status = "OK" if n == expected else "MISMATCH"
        failed = failed or n != expected
        print(f"  {status}: sent {n:,} of {expected:,}\n")

    if failed:
        sys.exit("At least one table did not match its file. Fix the cause and run again (loads are replace-style, so re-running is safe).")


if __name__ == "__main__":
    main()
