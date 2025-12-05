from flask import Blueprint, render_template, redirect, url_for, flash
from app.extensions import db
from app.models.note import Note
from app.models.comment import Comment
from app.forms.note_forms import CreateNoteForm, CommentForm
from app.utils.decorators import admin_only
from flask_login import current_user, login_required
from datetime import date

notes_bp = Blueprint("notes", __name__, template_folder="../templates/notes")

# Allow logged-in users to comment on notes
@notes_bp.route("/note/<int:note_id>", methods=["GET", "POST"])
def show_note(note_id):
    requested_note = db.get_or_404(Note, note_id)
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
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for("main.get_all_notes"))
    return render_template("make-note.html", form=form)


# Use a decorator so only an admin user can edit a note
@notes_bp.route("/edit-note/<int:note_id>", methods=["GET", "POST"])
@admin_only
def edit_note(note_id):
    note = db.get_or_404(Note, note_id)
    edit_form = CreateNoteForm(
        title=note.title,
        subtitle=note.subtitle,
        img_url=note.img_url,
        author=note.author,
        body=note.body
    )
    if edit_form.validate_on_submit():
        note.title = edit_form.title.data
        note.subtitle = edit_form.subtitle.data
        note.img_url = edit_form.img_url.data
        note.author = current_user
        note.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("notes.show_note", note_id=note.id))
    return render_template("make-note.html", form=edit_form, is_edit=True)


# Use a decorator so only an admin user can delete a note
@notes_bp.route("/delete/<int:note_id>")
@admin_only
def delete_note(note_id):
    note_to_delete = db.get_or_404(Note, note_id)
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for("main.get_all_notes"))