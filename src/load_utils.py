from datetime import datetime, timezone

from psycopg import sql

from db import get_engine


def replace_raw_table(table, columns, rows, source, column_types=None, log_every=250_000):
    """Atomically replace raw.<table> with `rows`, streamed via COPY.

    columns      -- column names, in the same order as each row
    rows         -- any iterable of tuples/lists (sqlite cursor, csv reader, generator)
    source       -- where the data came from, stored in _source
    column_types -- optional {column: postgres_type}; everything else is TEXT
    """
    column_types = column_types or {}
    temp = f"{table}__loading"
    loaded_at = datetime.now(timezone.utc)
    all_cols = list(columns) + ["_source", "_loaded_at"]

    raw_conn = get_engine().raw_connection()
    conn = raw_conn.driver_connection
    n = 0
    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("DROP TABLE IF EXISTS raw.{}").format(sql.Identifier(temp)))
            col_defs = sql.SQL(", ").join(
                sql.SQL("{} {}").format(sql.Identifier(c), sql.SQL(column_types.get(c, "TEXT")))
                for c in columns
            )
            cur.execute(sql.SQL(
                "CREATE TABLE raw.{} ({}, _source TEXT, _loaded_at TIMESTAMPTZ)"
            ).format(sql.Identifier(temp), col_defs))

            copy_sql = sql.SQL("COPY raw.{} ({}) FROM STDIN").format(
                sql.Identifier(temp), sql.SQL(", ").join(map(sql.Identifier, all_cols))
            )
            with cur.copy(copy_sql) as copy:
                for row in rows:
                    values = [None if v is None else str(v) for v in row]
                    copy.write_row(values + [source, loaded_at])
                    n += 1
                    if n % log_every == 0:
                        print(f"  {table}: {n:,} rows sent")

            # swap in, all-or-nothing
            cur.execute(sql.SQL("DROP TABLE IF EXISTS raw.{}").format(sql.Identifier(table)))
            cur.execute(sql.SQL("ALTER TABLE raw.{} RENAME TO {}").format(
                sql.Identifier(temp), sql.Identifier(table)))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        raw_conn.close()
    return n