from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, URL, Optional
from flask_ckeditor import CKEditorField
from app.i18n import lazy_translate

# WTForm for creating a note
class CreateNoteForm(FlaskForm):
    title = StringField(lazy_translate("form_note_title"), validators=[DataRequired()])
    subtitle = StringField(lazy_translate("form_note_subtitle"), validators=[DataRequired()])
    img_url = StringField(lazy_translate("form_note_image_url"), validators=[Optional(), URL()])
    book = StringField(lazy_translate("form_book"), validators=[Optional()])
    visibility = RadioField(
        lazy_translate("form_visibility"),
        choices=[("public", lazy_translate("form_visibility_public")), ("private", lazy_translate("form_visibility_private"))],
        validators=[DataRequired()],
        default="public",
    )
    body = CKEditorField(lazy_translate("form_note_content"), validators=[DataRequired()])
    submit = SubmitField(lazy_translate("form_submit_note"))

# Create a CommentForm so users can leave comments below notes
class CommentForm(FlaskForm):
    comment_text = CKEditorField(lazy_translate("form_comment"), validators=[DataRequired()])
    submit = SubmitField(lazy_translate("form_submit_comment"))