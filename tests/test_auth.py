"""Tests for registration, login, logout and route protection."""
import pytest

from app import db
from app.models import User
from tests.conftest import random_password


def register(client, username="carol", email="carol@example.com", password=None, confirm=None):
    password = password or random_password()
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm if confirm is not None else password,
        },
    )


class TestRegistration:
    def test_register_page_loads(self, client):
        assert client.get("/register").status_code == 200

    def test_successful_registration_hashes_password(self, client):
        password = random_password()
        response = register(client, password=password)

        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

        user = db.session.scalar(db.select(User).where(User.email == "carol@example.com"))
        assert user is not None
        assert user.password_hash != password
        assert password not in user.password_hash
        assert user.check_password(password)

    def test_duplicate_email_is_rejected(self, client, make_user):
        user, _ = make_user("dave", "dave@example.com")
        response = register(client, username="other", email=user.email)

        assert response.status_code == 200
        assert b"already registered" in response.data
        assert db.session.scalar(db.select(db.func.count(User.id))) == 1

    def test_duplicate_username_is_rejected_case_insensitively(self, client, make_user):
        make_user("Erin", "erin@example.com")
        response = register(client, username="erin", email="other@example.com")

        assert response.status_code == 200
        assert b"already taken" in response.data

    @pytest.mark.parametrize(
        "password",
        ["short1A", "onlyletterslong", "12345678901"],
        ids=["too-short", "no-digit", "no-letter"],
    )
    def test_weak_passwords_are_rejected(self, client, password):
        response = register(client, password=password)

        assert response.status_code == 200
        assert db.session.scalar(db.select(db.func.count(User.id))) == 0

    def test_password_confirmation_must_match(self, client):
        response = register(client, password=random_password(), confirm="Different-1234")

        assert response.status_code == 200
        assert b"Passwords must match" in response.data

    def test_invalid_email_and_username_are_rejected(self, client):
        response = register(client, username="bad name!", email="not-an-email")

        assert response.status_code == 200
        assert db.session.scalar(db.select(db.func.count(User.id))) == 0


class TestLogin:
    def test_login_page_loads(self, client):
        assert client.get("/login").status_code == 200

    def test_successful_login_reaches_dashboard(self, client, make_user, login):
        user, password = make_user("frank")
        response = login(user.email, password, follow_redirects=True)

        assert response.status_code == 200
        assert b"Welcome back, frank" in response.data

    def test_email_is_case_insensitive(self, client, make_user, login):
        user, password = make_user("grace")
        response = login(user.email.upper(), password)

        assert response.status_code == 302

    def test_wrong_password_is_rejected(self, client, make_user, login):
        user, _ = make_user("heidi")
        response = login(user.email, "Wrong-Password-1")

        assert response.status_code == 401
        assert b"Invalid email or password" in response.data
        assert client.get("/dashboard").status_code == 302

    def test_unknown_user_gets_same_generic_error(self, client, login):
        response = login("nobody@example.com", "Wrong-Password-1")

        assert response.status_code == 401
        assert b"Invalid email or password" in response.data

    def test_external_redirect_target_is_ignored(self, client, make_user, login):
        user, password = make_user("ivan")
        response = login(user.email, password, next="https://evil.example/phish")

        assert response.status_code == 302
        assert "evil.example" not in response.headers["Location"]

    def test_local_redirect_target_is_followed(self, client, make_user, login):
        user, password = make_user("judy")
        response = login(user.email, password, next="/tasks")

        assert response.headers["Location"].endswith("/tasks")

    def test_authenticated_user_is_redirected_away_from_login(self, client, alice):
        response = client.get("/login")

        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]


class TestLogout:
    def test_logout_requires_post(self, client, alice):
        assert client.get("/logout").status_code == 405

    def test_logout_ends_session(self, client, alice):
        response = client.post("/logout")

        assert response.status_code == 302
        assert "/login" in client.get("/dashboard").headers["Location"]


class TestAuthenticationProtection:
    @pytest.mark.parametrize(
        "path", ["/dashboard", "/tasks", "/tasks/new", "/tasks/1/edit"]
    )
    def test_private_pages_redirect_anonymous_users(self, client, path):
        response = client.get(path)

        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    @pytest.mark.parametrize(
        "path", ["/tasks/1/delete", "/tasks/1/complete", "/logout"]
    )
    def test_private_actions_reject_anonymous_posts(self, client, path):
        response = client.post(path)

        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_landing_page_is_public(self, client):
        assert client.get("/").status_code == 200

    def test_security_headers_are_set(self, client):
        response = client.get("/login")

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    def test_unknown_page_returns_friendly_404(self, client):
        response = client.get("/does-not-exist")

        assert response.status_code == 404
        assert b"Page not found" in response.data
