import os
import boto3
import uuid
from app.core.config import settings
from PIL import Image as PILImage
import io

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

    file_bytes = file.file.read()
    image = PILImage.open(io.BytesIO(file_bytes))

    # Resize (max 800px)
    image.thumbnail((800, 800))

    output = io.BytesIO()
    image.save(output, format=image.format)
    output.seek(0)

    # unique filename
    file_extension = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{file_extension}"

    # upload original (resize)
    s3.upload_fileobj(
        output,
        settings.AWS_S3_BUCKET,
        unique_name,
        ExtraArgs={"ContentType": file.content_type}
    )

    # create thumbnail
    thumb = image.copy()
    thumb.thumbnail((200, 200))

    thumb_bytes = io.BytesIO()
    thumb.save(thumb_bytes, format=image.format)
    thumb_bytes.seek(0)

    thumb_name = f"thumb_{unique_name}"

    s3.upload_fileobj(
        thumb_bytes,
        settings.AWS_S3_BUCKET,
        thumb_name,
        ExtraArgs={"ContentType": file.content_type}
    )

    file_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_name}"
    thumb_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{thumb_name}"

    return file_url, thumb_url


def save_local(file):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path