from minio import Minio
from app.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET_NAME,
    MINIO_SECURE
)

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


def create_bucket():
    if not client.bucket_exists(MINIO_BUCKET_NAME):
        client.make_bucket(MINIO_BUCKET_NAME)


def upload_file(file_path: str, object_name: str, content_type: str):
    create_bucket()

    client.fput_object(
        MINIO_BUCKET_NAME,
        object_name,
        file_path,
        content_type=content_type
    )


def delete_file(object_name: str):
    client.remove_object(
        MINIO_BUCKET_NAME,
        object_name
    )