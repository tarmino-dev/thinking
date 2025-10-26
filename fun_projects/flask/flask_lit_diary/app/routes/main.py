from flask import Blueprint, render_template
from app.extensions import db
from app.models.note import Note

main_bp = Blueprint("main", __name__, template_folder="../templates/main")

@main_bp.route('/')
def get_all_notes():
    result = db.session.execute(db.select(Note))
    notes = result.scalars().all()
    return render_template("index.html", all_notes=notes)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact")
def contact():
    return render_template("contact.html")