from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app
from app.extensions import db
from app.models.user import User
from app.forms.auth_forms import RegisterForm, LoginForm, DeleteAccountForm, ResetRequestForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer
from app.routes.main import send_email

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


def _generate_reset_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset')


def _verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt='password-reset', max_age=max_age)
    except Exception:
        return None

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash("You've already singed up with that email, log in instead!")
            return redirect(url_for("auth.login"))
        password = form.password.data
        name = form.name.data
        hash_and_salted_password = generate_password_hash(
            password=password,
            method="pbkdf2:sha256",
            salt_length=16
        )
        new_user = User(
            email=email,
            password=hash_and_salted_password,
            name=name
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("main.get_all_notes"))
    return render_template("register.html", form=form)


# Retrieve a user from the database based on their email. 
@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash("That email does not exist, please retry again.")
            return redirect(url_for("auth.login"))
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main.get_all_notes"))
        else:
            flash("Password incorrect, please try again.")
            return redirect(url_for("auth.login"))
    return render_template("login.html", form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.get_all_notes"))


@auth_bp.route('/account')
@login_required
def account():
    return render_template('account.html')


@auth_bp.route('/delete-account', methods=["GET", "POST"])
@login_required
def delete_account():
    if current_user.id == 1:
        abort(403)
    form = DeleteAccountForm()
    if form.validate_on_submit():
        user = db.session.get(User, current_user.id)
        db.session.delete(user)
        db.session.commit()
        logout_user()
        return redirect(url_for("main.get_all_notes"))
    return render_template("delete_account.html", form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user:
            token = _generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(
                subject="Password Reset – Literary Diary",
                body=(
                    f"Click the link below to reset your password:\n\n"
                    f"{reset_url}\n\n"
                    f"This link expires in 1 hour. If you did not request a reset, ignore this email."
                ),
                to_email=user.email,
            )
        flash("If that email is registered, a reset link has been sent.")
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = _verify_reset_token(token)
    if email is None:
        flash("The reset link is invalid or has expired.")
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            abort(404)
        user.password = generate_password_hash(
            password=form.password.data,
            method="pbkdf2:sha256",
            salt_length=16,
        )
        db.session.commit()
        flash("Your password has been updated. Please log in.")
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)