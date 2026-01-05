from flask import request, jsonify
from flask_login import current_user
from app.extensions import db
from app.models.note import Note
from app.api.v1 import api_v1
from app.api.serializers.note import note_list_schema, note_detail_schema
from datetime import date


@api_v1.get("/notes")
def get_notes():
    notes = Note.query.order_by(Note.id.desc()).all()

    return jsonify({
        "total": len(notes),
        "items": [note_list_schema(note) for note in notes]
    })

@api_v1.post("/notes")
def create_note():
    if not current_user.is_authenticated:
        return jsonify({"error": "authentication required"}), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "invalid JSON"}), 400

    required_fields = ("title", "subtitle", "body")
    missing = [field for field in required_fields if field not in data]

    if missing:
        return jsonify({
            "error": "validation error",
            "missing_fields": missing
        }), 400

    note = Note(
        title=data["title"],
        subtitle=data["subtitle"],
        body=data["body"],
        img_url=data.get("img_url"),
        author=current_user,
        date=date.today().strftime("%B %d, %Y")
    )

    db.session.add(note)
    db.session.commit()

    return jsonify(note_detail_schema(note)), 201

