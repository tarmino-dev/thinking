import os
import boto3
import uuid
from app.core.config import settings

def save_file(file):
    if settings.STORAGE_TYPE == "s3":
        return save_s3(file)
    else:
        return save_local(file)


def save_s3(file):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    file_extension = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{file_extension}"

    s3.upload_fileobj(
        file.file,
        settings.AWS_S3_BUCKET,
        unique_name,
        ExtraArgs={"ContentType": file.content_type}
    )

    file_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_name}"

    return file_url


def save_local(file):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path