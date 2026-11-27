
# Decision Log

This document records significant technical, analytical and engineering decisions made during the FleetPulse project.

## Decision 001: Project Repository Setup

**Status:** Accepted

**Context:**
The project requires a collaborative environment for cross-functional development.

**Decision:**
A dedicated GitHub repository will serve as the central workspace for source code, documentation, tests and project collaboration.

**Rationale:**
- Centralised version control.
- Collaborative development through branches and pull requests.
- Transparent documentation of engineering decisions.

**Consequences:**
All team contributions will be submitted through feature branches and pull requests.
Raw datasets and sensitive credentials will not be committed.


## Decision 002: Ingesting .csv and .jsonl files

**Status:** In-review

**Context:**
All columns load as TEXT. The metadata column is JSONB.

Empty CSV cells would be kept as empty strings, and staging decides what they mean. There are none in these files.

Missing GPS metadata is stored as NULL. The key is absent in those events, not set to null.

Each script checks the header (CSVs), field counts per row and unexpected GPS keys, and it stops the load rather than loading wrongly.

Each load compares its row count to the file, and the script exits with an error on a mismatch.

_source holds the plain file name, such as fuel_card_dispense_logs.csv

