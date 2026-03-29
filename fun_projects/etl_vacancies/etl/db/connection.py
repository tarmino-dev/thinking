from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@postgres:5432/"
    f"{os.environ['POSTGRES_DB']}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
