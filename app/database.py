import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

if settings.database_url:
    url = settings.database_url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    SQL_URL = url
else:
    password = urllib.parse.quote_plus(settings.database_password or "")
    SQL_URL = f"postgresql+psycopg2://{settings.database_username}:{password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine_args = {
    "pool_pre_ping": True,
}
# Only apply pool sizing for real PostgreSQL (skip SQLite if used in test fixtures)
if "sqlite" not in SQL_URL:
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 300
    })

engine = create_engine(url=SQL_URL, **engine_args)

LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()