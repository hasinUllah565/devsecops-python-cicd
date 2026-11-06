"""WTForms definitions with server-side validation."""
import re

from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

from app import db
from app.models import PRIORITY_LABELS, STATUS_LABELS, User

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(value):
    """Strip whitespace and drop control characters from user input."""
    if value is None:
        return value
    return _CONTROL_CHARS.sub("", value).strip()


def _lower_clean(value):
    value = clean_text(value)
    return value.lower() if value else value


def password_strength(_form, field):
    """Require at least one letter and one digit."""
    password = field.data or ""
    if not (re.search(r"[A-Za-z]", password) and re.search(r"\d", password)):
        raise ValidationError("Password must contain at least one letter and one number.")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[clean_text],
        validators=[
            DataRequired(),
            Length(min=3, max=32),
            Regexp(
                r"^[A-Za-z0-9_.-]+$",
                message="Use only letters, numbers, dots, dashes and underscores.",
            ),
        ],
    )
    email = StringField(
        "Email",
        filters=[_lower_clean],
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128), password_strength],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")

    def validate_username(self, field):
        exists = db.session.scalar(
            db.select(User).where(func.lower(User.username) == field.data.lower())
        )
        if exists:
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        exists = db.session.scalar(db.select(User).where(User.email == field.data))
        if exists:
            raise ValidationError("That email is already registered.")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        filters=[_lower_clean],
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class TaskForm(FlaskForm):
    title = StringField(
        "Title", filters=[clean_text], validators=[DataRequired(), Length(min=3, max=120)]
    )
    description = TextAreaField(
        "Description", filters=[clean_text], validators=[Optional(), Length(max=2000)]
    )
    priority = SelectField(
        "Priority",
        choices=list(PRIORITY_LABELS.items()),
        default="medium",
        validators=[DataRequired()],
    )
    status = SelectField(
        "Status",
        choices=list(STATUS_LABELS.items()),
        default="pending",
        validators=[DataRequired()],
    )
    due_date = DateField("Deadline", format="%Y-%m-%d", validators=[Optional()])
    submit = SubmitField("Save task")
