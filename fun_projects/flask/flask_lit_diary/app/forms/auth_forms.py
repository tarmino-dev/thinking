from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from app.i18n import lazy_translate

# Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField(lazy_translate("form_email"), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_translate("form_password"), validators=[DataRequired()])
    name = StringField(lazy_translate("form_name"), validators=[DataRequired()])
    submit = SubmitField(lazy_translate("form_sign_up"))


# Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField(lazy_translate("form_email"), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_translate("form_password"), validators=[DataRequired()])
    submit = SubmitField(lazy_translate("form_log_in"))


class DeleteAccountForm(FlaskForm):
    submit = SubmitField(lazy_translate("form_delete_account"))


class ResetRequestForm(FlaskForm):
    email = StringField(lazy_translate("form_email"), validators=[DataRequired(), Email()])
    submit = SubmitField(lazy_translate("form_send_reset_link"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(lazy_translate("form_new_password"), validators=[DataRequired()])
    confirm = PasswordField(lazy_translate("form_confirm_password"), validators=[DataRequired(), EqualTo('password', message=lazy_translate("form_passwords_must_match"))])
    submit = SubmitField(lazy_translate("form_set_new_password"))