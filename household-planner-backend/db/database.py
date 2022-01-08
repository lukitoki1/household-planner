import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from db.database_settings import db_settings

from db.database_settings import prod


def create_connection_engine():
    if prod:
        return create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="postgresql+pg8000",
                username=db_settings.POSTGRES_USER,
                password=db_settings.POSTGRES_PASSWORD,
                database=db_settings.POSTGRES_DB,
                query={
                    "unix_sock": "{}/{}/.s.PGSQL.5432".format(
                        "/cloudsql",
                        db_settings.POSTGRES_SERVER)
                }
            )
        )
    SQLALCHEMY_DATABASE_URL = db_settings.DATABASE_URL
    return create_engine(SQLALCHEMY_DATABASE_URL)


#prod
engine = create_connection_engine()
#test
# SQLALCHEMY_DATABASE_URL = db_settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
