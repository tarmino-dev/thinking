from flask import Blueprint, render_template, redirect, url_for, current_app, flash, session, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.note import Note
from app.forms.contact_forms import ContactForm
from app.i18n import translate, LANGUAGES
import requests

main_bp = Blueprint("main", __name__, template_folder="../templates/main")

PER_PAGE = 10


def _paginate(stmt):
    """Paginate a notes select statement using the ?page query parameter.

    Non-numeric page values fall back to 1 (via type=int); values below 1 are
    clamped. error_out=False keeps out-of-range pages from raising a 404.
    """
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    return db.paginate(stmt, page=page, per_page=PER_PAGE, error_out=False)


@main_bp.route('/')
def get_all_notes():
    pagination = _paginate(
        db.select(Note).where(Note.is_public.is_(True)).order_by(Note.id.desc())
    )
    return render_template("index.html", all_notes=pagination.items, pagination=pagination, is_my_notes=False)


@main_bp.route("/my-notes")
@login_required
def my_notes():
    pagination = _paginate(
        db.select(Note).where(Note.author_id == current_user.id).order_by(Note.id.desc())
    )
    return render_template("index.html", all_notes=pagination.items, pagination=pagination, is_my_notes=True)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        subject = "New message in the Literary Diary Conctact Form"
        body = f"Name: {form.name.data}\nEmail: {form.email.data}\nMessage: {form.message.data}"
        success = send_email(subject=subject, body=body)
        if success:
            flash(translate("flash_message_sent"), "success")
        else:
            flash(translate("flash_message_failed"), "error")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)

@main_bp.route("/api-docs")
def api_docs():
    return render_template("api.html")


@main_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in LANGUAGES:
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.get_all_notes"))

def send_email(subject, body, to_email=None):
    """
    Sends an email using SendGrid API.
    Returns True if successful, otherwise False.
    """
    api_key = current_app.config["SENDGRID_API_KEY"]
    from_email = current_app.config["GMAIL_EMAIL"]
    to_email = to_email or from_email

    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "personalizations": [
            {"to": [{"email": to_email}]}
        ],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 202:
            return True
        else:
            current_app.logger.error(f"SendGrid error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}") # Flask outputs this to Render Logs by default.
        return False