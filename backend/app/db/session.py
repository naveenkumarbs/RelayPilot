from collections.abc import Generator 
from sqlite3 import Connection

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL 
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

database_path = settings.resolved_database_path 
database_path.parent.mkdir(parents=True, exist_ok=True)

database_url = URL.create(
    drivername="sqlite+pysqlite",
    database=str(database_path),
)

engine = create_engine(
    database_url,
    connect_args={
        "check_same_thread": False, 
        "timeout": settings.database_timeout_seconds,
    },
    echo=False,
    hide_parameters=True,
)

@event.listens_for(engine, "connect")
def enable_foreign_keys(
    dbapi_connection: Connection, 
    connection_record: object,
) -> None : 
    cursor = dbapi_connection.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False)

def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
