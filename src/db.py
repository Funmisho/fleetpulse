import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL

load_dotenv()

def get_engine(role: str | None = "fleet_writer"):
    """Engine for the FleetPulse database.

    By default every session switches to fleet_writer, so tables created
    by the pipeline are owned by the group, not by one person.
    """
    url = URL.create(
        "postgresql+psycopg",
        username=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ["PGHOST"],
        port=int(os.getenv("PGPORT", 5432)),
        database=os.environ["PGDATABASE"],
        query={"sslmode": os.getenv("PGSSLMODE", "require")},
    )
    engine = create_engine(url, pool_pre_ping=True)

    if role:
        @event.listens_for(engine, "connect")
        def _set_role(dbapi_conn, _record):
            with dbapi_conn.cursor() as cur:
                cur.execute(f"SET ROLE {role}")
            dbapi_conn.commit()  # without this, the role is undone when the pool resets

    return engine


# URL.create handles special characters in your password safely.
# The SET ROLE here applies the fleet_writer convention automatically, so nobody has to remember it.