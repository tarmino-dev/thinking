from flask import jsonify
from flask_login import current_user
from app.api.v1 import api_v1
from app.api.serializers.note import note_export_schema, comment_export_schema


@api_v1.get("/export")
def export_data():
    if not current_user.is_authenticated:
        return jsonify({"error": "authentication required"}), 401

    return jsonify({
        "profile": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
        },
        "notes": [note_export_schema(n) for n in current_user.notes],
        "comments": [comment_export_schema(c) for c in current_user.comments],
    })
