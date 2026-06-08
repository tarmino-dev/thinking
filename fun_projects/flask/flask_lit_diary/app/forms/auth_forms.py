from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

# Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("SIGN ME UP!")


# Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("LET ME IN!")


class DeleteAccountForm(FlaskForm):
    submit = SubmitField("DELETE MY ACCOUNT")


class ResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("SEND RESET LINK")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("SET NEW PASSWORD")