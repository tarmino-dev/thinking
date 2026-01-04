from flask import jsonify
from app.models.note import Note
from app.api.v1 import api_v1
from app.api.serializers.note import note_list_schema


@api_v1.get("/notes")
def get_notes():
    notes = Note.query.order_by(Note.id.desc()).all()

    return jsonify({
        "total": len(notes),
        "items": [note_list_schema(note) for note in notes]
    })
