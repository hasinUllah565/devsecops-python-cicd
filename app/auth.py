"""Authentication blueprint: registration, login and logout."""
import secrets
from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User

auth_bp = Blueprint("auth", __name__)

# Checked when the email is unknown so response timing does not reveal
# whether an account exists.
_DUMMY_HASH = generate_password_hash(secrets.token_hex(16))


def is_safe_url(target) -> bool:
    """Allow redirects only to relative paths on this host (blocks open redirects)."""
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("That username or email is already in use.", "danger")
            return render_template("register.html", form=form), 409
        flash("Account created. You can sign in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data))
        if user is not None:
            valid = user.check_password(form.password.data)
        else:
            check_password_hash(_DUMMY_HASH, form.password.data)
            valid = False

        if valid:
            session.clear()
            login_user(user, remember=form.remember.data)
            session.permanent = True
            next_url = request.args.get("next")
            if is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for("main.dashboard"))

        # One generic message for every failure mode.
        flash("Invalid email or password.", "danger")
        return render_template("login.html", form=form), 401

    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
