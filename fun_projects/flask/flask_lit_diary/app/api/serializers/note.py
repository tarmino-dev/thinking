from app.models.note import Note


def note_list_schema(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "subtitle": note.subtitle,
        "date": note.date,
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
        "date": note.date,
        "body": note.body,
        "img_url": note.img_url,
        "author": {
            "id": note.author.id,
            "name": note.author.name,
        },
    }
