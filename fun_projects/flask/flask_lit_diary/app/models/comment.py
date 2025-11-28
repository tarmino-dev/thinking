from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, ForeignKey

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_notes.id"))
    # These are not columns, but a logical relationship between tables.
    comment_author: Mapped["User"] = relationship("User", back_populates="comments")
    parent_note: Mapped["Note"] = relationship("Note", back_populates="comments")