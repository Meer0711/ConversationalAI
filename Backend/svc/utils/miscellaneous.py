import os
import random
import tempfile
import urllib.parse

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from azure.storage.blob import generate_blob_sas, BlobSasPermissions, BlobClient
from datetime import datetime, timedelta
from svc import settings


def convert_to_lowercase_without_spaces(input_string):
    output_string = input_string.replace(" ", "").lower()
    return output_string


def get_random_message():
    subjects = ["The system", "Our service", "The application", "This bot"]
    verbs = ["is currently", "will be", "was"]
    adjectives = ["undergoing maintenance", "unavailable"]
    times = ["shortly", "tomorrow", "as soon as possible"]

    subject = random.choice(subjects)
    verb = random.choice(verbs)
    adjective = random.choice(adjectives)
    time = random.choice(times)

    return f"{subject} {verb} {adjective} {time}."


def get_blob_url_with_sas(blob_name):
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_ACCOUNT_NAME,
        account_key=settings.AZURE_ACCOUNT_KEY,
        container_name=settings.CONTAINER_NAME,
        blob_name=blob_name,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now() + timedelta(hours=24),
    )
    return (
        f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/"
        f"{settings.CONTAINER_NAME}/{blob_name}?{sas_token}"
    )


def get_file_path(filename):
    temp_dir = tempfile.mkdtemp()
    blob_url = get_blob_url_with_sas(filename)
    parsed_url = urllib.parse.urlparse(blob_url)
    blob_path = parsed_url.path.lstrip("/")
    _, blob_name = blob_path.split("/", 1)
    local_file_path = os.path.join(temp_dir, blob_name.replace("/", "_"))
    blob_client = BlobClient.from_blob_url(blob_url)
    with open(local_file_path, "wb") as file:
        download_stream = blob_client.download_blob()
        file.write(download_stream.readall())
    return local_file_path


def create_account_vector_db(dbname):
    engine_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
    )
    engine = create_engine(engine_url)

    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT")
        try:
            connection.execute(text(f"CREATE DATABASE {dbname}"))
        except SQLAlchemyError as exc:
            raise exc
