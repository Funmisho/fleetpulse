from sqlalchemy import text
from db import get_engine

with get_engine().connect() as conn:
    row = conn.execute(text(
        "SELECT session_user, current_user, current_database(), version()"
    )).one()
    print(f"logged in as : {row[0]}")
    print(f"acting as    : {row[1]}")
    print(f"database     : {row[2]}")
    print(row[3].split(",")[0])