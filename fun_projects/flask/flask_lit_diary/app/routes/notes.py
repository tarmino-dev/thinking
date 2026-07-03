from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify, current_app
from app.extensions import db
from app.models.note import Note
from app.models.comment import Comment
from app.forms.note_forms import CreateNoteForm, CommentForm
from app import ai, images
from app.i18n import translate
from flask_login import current_user, login_required
from datetime import date
import anthropic

notes_bp = Blueprint("notes", __name__, template_folder="../templates/notes")

# Bounds for the AI discussion endpoint, to keep token cost predictable.
DISCUSS_MAX_MESSAGES = 20
DISCUSS_MAX_CHARS = 4000


def _can_edit_note(note: Note) -> bool:
    if not current_user.is_authenticated:
        return False
    return note.author_id == current_user.id or current_user.id == 1


# Allow logged-in users to comment on notes
@notes_bp.route("/note/<int:note_id>", methods=["GET", "POST"])
def show_note(note_id):
    requested_note = db.get_or_404(Note, note_id)
    if not requested_note.is_visible_to(current_user):
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment")
            return redirect(url_for("auth.login"))
        new_comment = Comment(
            text = form.comment_text.data,
            comment_author = current_user,
            parent_note = requested_note
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("notes.show_note", note_id=note_id))
    return render_template("note.html", note=requested_note, form=form)


# Use a decorator so only an admin user can create a new note
@notes_bp.route("/new-note", methods=["GET", "POST"])
@login_required
def add_new_note():
    form = CreateNoteForm()
    if form.validate_on_submit():
        new_note = Note(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            book=form.book.data,
            is_public=(form.visibility.data == "public"),
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for("main.get_all_notes"))
    return render_template("make-note.html", form=form)


@notes_bp.route("/edit-note/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = db.get_or_404(Note, note_id)
    if not _can_edit_note(note):
        abort(403)
    edit_form = CreateNoteForm(
        title=note.title,
        subtitle=note.subtitle,
        img_url=note.img_url,
        book=note.book or "",
        visibility="public" if note.is_public else "private",
        body=note.body,
    )
    if edit_form.validate_on_submit():
        note.title = edit_form.title.data
        note.subtitle = edit_form.subtitle.data
        note.img_url = edit_form.img_url.data
        note.book = edit_form.book.data
        note.is_public = edit_form.visibility.data == "public"
        note.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("notes.show_note", note_id=note.id))
    return render_template("make-note.html", form=edit_form, is_edit=True)


@notes_bp.route("/delete/<int:note_id>")
@login_required
def delete_note(note_id):
    note_to_delete = db.get_or_404(Note, note_id)
    if not _can_edit_note(note_to_delete):
        abort(403)
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for("main.get_all_notes"))


def _own_note_or_403(note_id):
    """Fetch a note and ensure the current user is its author (own notes only)."""
    note = db.get_or_404(Note, note_id)
    if note.author_id != current_user.id:
        abort(403)
    return note


@notes_bp.route("/note/<int:note_id>/discuss")
@login_required
def discuss_page(note_id):
    note = _own_note_or_403(note_id)
    return render_template("discuss.html", note=note)


@notes_bp.route("/note/<int:note_id>/discuss", methods=["POST"])
@login_required
def discuss_message(note_id):
    note = _own_note_or_403(note_id)

    data = request.get_json(silent=True) or {}
    raw_messages = data.get("messages")
    if not isinstance(raw_messages, list):
        return jsonify({"error": "invalid request"}), 400

    # Keep only the most recent, well-formed messages and cap their length.
    history = []
    for message in raw_messages[-DISCUSS_MAX_MESSAGES:]:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            history.append({"role": role, "content": content[:DISCUSS_MAX_CHARS]})

    if not history or history[-1]["role"] != "user":
        return jsonify({"error": "invalid request"}), 400

    try:
        reply = ai.discuss_note(note, history)
    except anthropic.AnthropicError:
        current_app.logger.exception("AI discussion failed")
        return jsonify({"error": "AI service unavailable"}), 502

    return jsonify({"reply": reply})


@notes_bp.route("/note/<int:note_id>/generate-image", methods=["POST"])
@login_required
def generate_image(note_id):
    note = _own_note_or_403(note_id)
    try:
        note.img_url = images.generate_note_image(note)
        db.session.commit()
        flash(translate("flash_image_generated"), "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Image generation failed")
        flash(translate("flash_image_failed"), "error")
    return redirect(url_for("notes.show_note", note_id=note.id))