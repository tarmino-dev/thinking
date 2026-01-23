from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from app.extensions import db
from app.models.note import Note
from app.forms.contact_forms import ContactForm
import requests

main_bp = Blueprint("main", __name__, template_folder="../templates/main")

@main_bp.route('/')
def get_all_notes():
    result = db.session.execute(db.select(Note))
    notes = result.scalars().all()
    return render_template("index.html", all_notes=notes)


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
            flash("Your message has been sent successfully!", "success")
        else:
            flash("Something went wrong. Please try again later.", "error")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)

@main_bp.route("/api-docs")
def api_docs():
    return render_template("api.html")

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