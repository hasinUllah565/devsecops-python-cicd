
"""Authentication blueprint: registration, login and logout."""

import secrets
from urllib.parse import urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User


auth_bp = Blueprint("auth", __name__)


# Dummy password hash helps reduce timing differences
# when an email address does not exist.
_DUMMY_HASH = generate_password_hash(secrets.token_hex(32))


def is_safe_url(target):
    """Allow only safe relative URLs for post-login redirects."""

    if not target:
        return False

    # Reject backslashes and protocol-relative URLs.
    if "\\" in target or target.startswith("//"):
        return False

    parsed_url = urlparse(target)

    # Reject external URLs and unsupported schemes.
    if parsed_url.scheme or parsed_url.netloc:
        return False

    # Only allow paths starting with a single slash.
    return parsed_url.path.startswith("/") and not parsed_url.path.startswith("//")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.tasks"))

    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(
            username=form.username.data,
            email=form.email.data,
        )

        user.set_password(form.password.data)

        db.session.add(user)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            flash(
                "That username or email is already in use.",
                "danger",
            )

            return render_template(
                "register.html",
                form=form,
            ), 409

        flash(
            "Account created. You can sign in now.",
            "success",
        )

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = db.session.scalar(
            db.select(User).where(
                User.email == form.email.data
            )
        )

        if user is not None:
            valid = user.check_password(form.password.data)
        else:
            check_password_hash(
                _DUMMY_HASH,
                form.password.data,
            )
            valid = False

        if valid:

            # Clear the previous session before authentication.
            session.clear()

            login_user(
                user,
                remember=form.remember.data,
            )

            # Respect the user's remember-me preference.
            session.permanent = bool(form.remember.data)

            next_url = request.args.get("next")

            if is_safe_url(next_url):
                return redirect(next_url)

            return redirect(url_for("main.dashboard"))

        # Generic error prevents revealing whether an account exists.
        flash(
            "Invalid email or password.",
            "danger",
        )

        return render_template(
            "login.html",
            form=form,
        ), 401

    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()
    session.clear()

    flash(
        "You have been signed out.",
        "info",
    )

    return redirect(url_for("auth.login"))

