from fastapi import APIRouter, UploadFile, File
from app.services.storage import save_file
from app.db.session import SessionLocal
from app.db.models import Image

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    db = SessionLocal()

    file_url, thumb_url = save_file(file)

    image = Image(filename=file.filename, path=file_url)
    db.add(image)
    db.commit()
    db.refresh(image)

    return {"id": image.id, "filename": image.filename}

@router.get("/images")
def get_images():
    db = SessionLocal()
    return db.query(Image).all()

@router.get("/images/{image_id}")
def get_image(image_id: int):
    return {"id": image_id}