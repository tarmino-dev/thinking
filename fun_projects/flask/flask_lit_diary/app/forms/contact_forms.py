from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField
from app.i18n import lazy_translate

# WTForm for sending feedback about the website
class ContactForm(FlaskForm):
    name = StringField(lazy_translate("form_name"), validators=[DataRequired()])
    email = StringField(lazy_translate("form_email_address"), validators=[DataRequired(), Email()])
    message = CKEditorField(lazy_translate("form_message"), validators=[DataRequired()])
    submit = SubmitField(lazy_translate("form_submit_message"))