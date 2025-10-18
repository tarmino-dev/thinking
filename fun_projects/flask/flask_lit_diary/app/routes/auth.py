from flask import Blueprint, render_template, redirect, url_for, flash
from app.extensions import db
from app.models.user import User
from app.forms.auth_forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash("You've already singed up with that email, log in instead!")
            return redirect(url_for("main.login"))
        password = form.password.data
        name = form.name.data
        hash_and_salted_password = generate_password_hash(
            password=password,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            email=email,
            password=hash_and_salted_password,
            name=name
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("main.get_all_posts"))
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
            return redirect(url_for("main.login"))
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main.get_all_posts"))
        else:
            flash("Password incorrect, please try again.")
            return redirect(url_for("main.login"))
    return render_template("login.html", form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.get_all_posts"))