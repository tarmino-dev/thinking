import base64
from fastapi import APIRouter, UploadFile, File
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.tasks import process_image
from app.db.session import SessionLocal
from app.db.models import Image, User
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import Depends
from app.api.dependencies import get_current_user, get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.image import ImageOut
from fastapi import HTTPException
from typing import List

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...),
                       user=Depends(get_current_user)):

    data = await file.read()
    task = process_image.delay(
        base64.b64encode(data).decode(), file.filename, file.content_type, user.id
    )

    return {"task_id": task.id}

@router.get("/tasks/{task_id}")
def get_task(task_id: str, user=Depends(get_current_user)):
    res = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": res.status,
        "result": res.result if res.ready() else None,
    }

@router.get("/images", response_model=List[ImageOut])
def get_images(user=Depends(get_current_user), db=Depends(get_db)):
    return db.query(Image).filter(Image.user_id == user.id).all()

@router.get("/images/{image_id}", response_model=ImageOut)
def get_image(image_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    image = db.query(Image).filter(
        Image.id == image_id, Image.user_id == user.id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.post("/register")
def register(user: UserCreate, db=Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return {"msg": "user created"}


@router.post("/login")
def login(user: UserLogin, db=Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})

    return {"access_token": token}
