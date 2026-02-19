from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@host.docker.internal:5432/etl"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
