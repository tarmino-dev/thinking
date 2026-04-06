from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    path = Column(String)