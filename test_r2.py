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

print("Endpoint:", R2_ENDPOINT)
print("Bucket:", R2_BUCKET_NAME)

response = client.list_objects_v2(
    Bucket=R2_BUCKET_NAME
)

print("R2 connection successful!")
print(response)