from app.models.note import Note
from app.models.comment import Comment


def note_list_schema(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "subtitle": note.subtitle,
        "book": note.book,
        "date": note.date,
        "is_public": note.is_public,
        "author": {
            "id": note.author.id,
            "name": note.author.name,
        },
    }


def note_detail_schema(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "subtitle": note.subtitle,
        "book": note.book,
        "date": note.date,
        "body": note.body,
        "img_url": note.img_url,
        "is_public": note.is_public,
        "author": {
            "id": note.author.id,
            "name": note.author.name,
        },
    }


def note_export_schema(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "subtitle": note.subtitle,
        "date": note.date,
        "body": note.body,
        "img_url": note.img_url,
        "book": note.book,
        "is_public": note.is_public,
    }


def comment_export_schema(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "text": comment.text,
        "note_id": comment.note_id,
        "note_title": comment.parent_note.title,
    }
