import os
from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR

def save_file(file):
    if settings.STORAGE_TYPE == "local":
        return save_local(file)
    else:
        raise NotImplementedError("S3 not implemented yet")


def save_local(file):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path