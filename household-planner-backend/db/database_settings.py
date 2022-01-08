import os
import hashlib
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()
PROJECT_ID = "household-planner-333519"
SECRET_ID = "database-password"


def access_secret_version(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')


def get_db_pass(is_prod):
    if is_prod:
        db_pass = access_secret_version(SECRET_ID)
        return db_pass
    return os.getenv("POSTGRES_PASSWORD")


prod = (os.getenv('PROD', 'False') == 'True')


class DbSettings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = get_db_pass(prod)
    # POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "household_db")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


db_settings = DbSettings()
