from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    return {"filename": file.filename}

@router.get("/images")
def get_images():
    return []

@router.get("/images/{image_id}")
def get_image(image_id: int):
    return {"id": image_id}