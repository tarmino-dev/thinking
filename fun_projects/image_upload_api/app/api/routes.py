from fastapi import APIRouter, UploadFile, File
from app.services.storage import save_file
from app.db.session import SessionLocal
from app.db.models import Image, User
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import Depends
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user=Depends(get_current_user)):
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

@router.post("/register")
def register(username: str, password: str):
    db = SessionLocal()

    user = User(
        username=username,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return {"msg": "user created"}


@router.post("/login")
def login(username: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password):
        return {"error": "invalid credentials"}

    token = create_access_token({"sub": user.username})

    return {"access_token": token}
