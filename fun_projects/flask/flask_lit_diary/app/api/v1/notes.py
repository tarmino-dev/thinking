from flask import jsonify
from app.models.note import Note
from app.api.v1 import api_v1


@api_v1.get("/notes")
def get_notes():
    notes = Note.query.all()

    return jsonify([
        {
            "id": note.id,
            "title": note.title,
            "subtitle": note.subtitle,
            "date": note.date,
            "author": {
                "id": note.author.id,
                "name": note.author.name
            }
        }
        for note in notes
    ])
