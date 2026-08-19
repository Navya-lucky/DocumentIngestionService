import boto3

from app.config import (
    R2_ENDPOINT,
    R2_ACCESS_KEY,
    R2_SECRET_KEY,
    R2_BUCKET_NAME
)


client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name="auto"
)


def upload_file(
    file_path: str,
    object_name: str,
    content_type: str
):
    client.upload_file(
        file_path,
        R2_BUCKET_NAME,
        object_name,
        ExtraArgs={
            "ContentType": content_type
        }
    )


def delete_file(object_name: str):
    client.delete_object(
        Bucket=R2_BUCKET_NAME,
        Key=object_name
    )