from app.models.note import Note


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
