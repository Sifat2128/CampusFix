from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from . config import settings
import urllib.parse 

password = urllib.parse.quote_plus(settings.database_password)
SQL_URL = f"postgresql+psycopg2://{settings.database_username}:{password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine = create_engine(url=SQL_URL)

LocalSession = sessionmaker(bind = engine)

Base = declarative_base()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()