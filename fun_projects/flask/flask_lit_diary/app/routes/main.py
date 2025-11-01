from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from app.extensions import db
from app.models.note import Note
from app.forms.contact_forms import ContactForm
import smtplib

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
        email_msg = f"Subject: New message in the Literary Diary Conctact Form\n\nName: {form.name.data}\nEmail: {form.email.data}\nMessage: {form.message.data}"
        success = send_email(email_msg)
        if success:
            flash("Your message has been sent successfully!", "success")
        else:
            flash("Something went wrong. Please try again later.", "error")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)

def send_email(message):
    try:
        smtp_address = current_app.config["GMAIL_SMTP_ADDRESS"]
        email = current_app.config["GMAIL_EMAIL"]
        password = current_app.config["GMAIL_APP_PASSWORD"]
        with smtplib.SMTP(smtp_address) as connection:
            connection.starttls()
            connection.login(user=email, password=password)
            connection.sendmail(from_addr=email,
                                to_addrs=email, msg=message)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}") # Flask outputs this to Render Logs by default.
        return False