from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

# WTForm for creating a note
class CreateNoteForm(FlaskForm):
    title = StringField("Note Title", validators=[DataRequired()])
    subtitle = StringField("Note Subtitle", validators=[DataRequired()])
    img_url = StringField("Note Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Note Content", validators=[DataRequired()])
    submit = SubmitField("Submit Note")

# Create a CommentForm so users can leave comments below notes
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")