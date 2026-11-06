"""Shared pytest fixtures."""
import secrets

import pytest

from app import create_app, db
from app.models import Task, User
from config import TestingConfig


def random_password() -> str:
    """Generate a throw-away password that satisfies the strength rules."""
    return "Aa1-" + secrets.token_urlsafe(9)


@pytest.fixture()
def app():
    """Application with a fresh in-memory database for every test."""
    application = create_app(TestingConfig)
    with application.app_context():
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(app):
    """Create a user directly in the database; returns (user, plain_password)."""

    def _make(username="alice", email=None):
        password = random_password()
        user = User(username=username, email=email or f"{username}@example.com")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, password

    return _make


@pytest.fixture()
def login(client):
    """Return a helper that signs a user in through the real login form."""

    def _login(email, password, test_client=None, follow_redirects=False, **params):
        target = test_client or client
        return target.post(
            "/login",
            data={"email": email, "password": password},
            query_string=params or None,
            follow_redirects=follow_redirects,
        )

    return _login


@pytest.fixture()
def alice(client, make_user, login):
    """A user who is already signed in on the default test client."""
    user, password = make_user("alice")
    login(user.email, password)
    return user


@pytest.fixture()
def bob_client(app, make_user, login):
    """A second, independently signed-in client for ownership tests."""
    user, password = make_user("bob")
    other = app.test_client()
    login(user.email, password, test_client=other)
    return other, user


@pytest.fixture()
def make_task(app):
    """Insert a task straight into the database for the given user."""

    def _make(user, title="Write report", **fields):
        task = Task(
            title=title,
            description=fields.pop("description", ""),
            priority=fields.pop("priority", "medium"),
            due_date=fields.pop("due_date", None),
            user_id=user.id,
        )
        task.set_status(fields.pop("status", "pending"))
        db.session.add(task)
        db.session.commit()
        return task

    return _make
