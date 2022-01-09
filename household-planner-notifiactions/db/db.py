import os
import hashlib
import sqlalchemy

from dotenv import load_dotenv
from google.cloud import secretmanager
from sqlalchemy import create_engine

load_dotenv()
PROJECT_ID = "household-planner-333519"
SECRET_ID = "database-password"

prod = (os.getenv('PROD', 'False') == 'True')

def access_secret_version(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

class DbSettings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = access_secret_version(SECRET_ID)
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "household-planner")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    print(DATABASE_URL)


db_settings = DbSettings()


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


engine = create_connection_engine()