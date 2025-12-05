from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey

class Note(db.Model):
    __tablename__ = "blog_notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    # These are not columns, but a logical relationship between tables.
    author: Mapped["User"] = relationship("User", back_populates="notes")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent_note")