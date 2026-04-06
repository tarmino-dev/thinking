from fastapi import FastAPI
from app.api.routes import router
from app.db.session import engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(router)