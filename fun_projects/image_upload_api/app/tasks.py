import base64

from app.celery_app import celery_app
from app.services.storage import save_file
from app.db.session import SessionLocal
from app.db.models import Image


@celery_app.task
def add(x, y):
    return x + y


@celery_app.task
def process_image(file_b64, filename, content_type, user_id):
    data = base64.b64decode(file_b64)
    file_url = save_file(data, filename, content_type)

    db = SessionLocal()
    try:
        image = Image(filename=filename, path=file_url, user_id=user_id)
        db.add(image)
        db.commit()
        db.refresh(image)
        return {"id": image.id, "filename": image.filename, "path": image.path}
    finally:
        db.close()
