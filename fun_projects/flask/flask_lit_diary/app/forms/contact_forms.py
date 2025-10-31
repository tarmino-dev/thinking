from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField

# WTForm for sending feedback about the website
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email address", validators=[DataRequired(), Email()])
    message = CKEditorField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit Message")