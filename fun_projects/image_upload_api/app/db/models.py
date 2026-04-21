from sqlalchemy import Column, Integer, String
from app.db.session import Base
from sqlalchemy import Boolean

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    path = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)