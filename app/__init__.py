"""Application factory for the Secure Task Management System."""
import logging
from datetime import datetime, timezone

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

CONTENT_SECURITY_POLICY = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self' https://cdn.jsdelivr.net",
        "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "font-src 'self' https://cdnjs.cloudflare.com",
        "img-src 'self' data:",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
)


def create_app(config_class=Config):
    """Build and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    # Importing models registers the user loader and the tables.
    from app import models  # noqa: F401
    from app.auth import auth_bp
    from app.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    _register_error_handlers(app)
    _register_security_headers(app)

    @app.context_processor
    def inject_globals():
        return {"now_year": datetime.now(timezone.utc).year}

    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)

    # Create the database on first start.
    with app.app_context():
        db.create_all()

    return app


def _register_security_headers(app):
    """Attach defensive HTTP headers to every response."""

    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return response


def _register_error_handlers(app):
    """Render friendly pages without leaking internal details."""

    messages = {
        400: ("Bad request", "The request could not be understood. Please try again."),
        403: ("Access denied", "You do not have permission to view this page."),
        404: ("Page not found", "The page you are looking for does not exist."),
        413: ("Request too large", "The submitted data is too large."),
    }

    def make_handler(code):
        title, message = messages[code]

        def handler(_error):
            return render_template("errors.html", code=code, title=title, message=message), code

        return handler

    for status_code in messages:
        app.register_error_handler(status_code, make_handler(status_code))

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        app.logger.exception("Unhandled server error")
        return (
            render_template(
                "errors.html",
                code=500,
                title="Something went wrong",
                message="An unexpected error occurred. Please try again later.",
            ),
            500,
        )
