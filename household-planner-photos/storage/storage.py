from google.cloud import storage
import datetime
import os
import google.auth
from google.auth.transport import requests

from model.file import File

bucket = None


def blob_initialize():
    global bucket
    bucket = storage.Client().bucket(os.getenv("IMAGE_BUCKET"))


def get_bucket():
    return bucket


def exist_folder(name: str):
    for blob in get_bucket().list_blobs():
        if blob.name.split("/")[0] == name:
            return True
    return False


def exist_file(folder_name: str, file_name: str):
    blob_name = f"{folder_name}/{file_name}"
    for blob in get_bucket().list_blobs():
        if blob.name == blob_name:
            return True
    return False


def create_blob(name: str, file_name: str):
    return get_bucket().blob(f"{name}/{file_name}")


def get_folder_files(name: str):
    client = storage.Client()
    buck = client.bucket(os.getenv("IMAGE_BUCKET"))
    credentials, project_id = google.auth.default()
    auth_request = requests.Request()
    credentials.refresh(auth_request)

    list = []
    for blob in buck.list_blobs(prefix=f"{name}/"):
        list.append(File(name=blob.name.split("/")[-1], url=blob.generate_signed_url(
            version="v2",
            expiration=datetime.timedelta(minutes=15),
            method="GET",
            service_account_email=os.getenv("SERVICE_ACCOUNT_MAIL"),
            access_token=credentials.token
        )))

    return list


def get_file(name: str, file_name: str):
    client = storage.Client()
    buck = client.bucket(os.getenv("IMAGE_BUCKET"))
    credentials, project_id = google.auth.default()
    auth_request = requests.Request()
    credentials.refresh(auth_request)

    blob = buck.blob(f"{name}/{file_name}")

    return File(name=blob.name.split("/")[-1], url=blob.generate_signed_url(
            version="v2",
            expiration=datetime.timedelta(minutes=15),
            method="GET",
            service_account_email=os.getenv("SERVICE_ACCOUNT_MAIL"),
            access_token=credentials.token
        ))
