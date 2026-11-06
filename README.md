# Secure Task Management System

A modern, responsive task manager built with **Flask**, **SQLAlchemy** and **SQLite**.
It is the application source for a DevSecOps CI/CD project (`devsecops-python-cicd`).

## Features

- **Authentication**: registration, login, logout, hashed passwords, secure sessions, form validation
- **Dashboard**: totals, completed / in-progress / pending counts, completion donut chart,
  open-task priority meters, recent tasks, upcoming deadlines, overdue count
- **Tasks**: create, view, edit, delete, mark completed, priorities (Low / Medium / High),
  deadlines, descriptions, filtering by status and priority, search, sorting, pagination
- **UI**: SaaS-style layout with sidebar, top bar, light and dark mode, mobile-friendly offcanvas menu

## Project structure

```text
devsecops-python-cicd/
├── app/
│   ├── __init__.py        # application factory, security headers, error handlers
│   ├── models.py          # User and Task models
│   ├── auth.py            # register / login / logout blueprint
│   ├── routes.py          # dashboard and task blueprint
│   ├── forms.py           # validated WTForms
│   ├── templates/         # Jinja2 templates
│   └── static/            # css/, js/, images/
├── tests/                 # pytest suite
├── config.py              # environment-driven configuration
├── run.py                 # development entry point
├── requirements.txt
├── pytest.ini
├── .env.example
└── .gitignore
```

## Run locally on Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Generate a secret key and paste it into .env as SECRET_KEY:
python3 -c "import secrets; print(secrets.token_hex(32))"

python run.py
```

Open <http://127.0.0.1:5000>. The SQLite database (`instance/app.db`) is created automatically on first start.

## Run the tests

```bash
pytest -v
```

The suite covers registration, login, invalid logins, authentication protection, task create /
update / delete, filtering and search, dashboard statistics, and cross-user authorization.

## Configuration

All settings come from environment variables (see `.env.example`). Nothing secret is hardcoded.

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Signs sessions and CSRF tokens | random per start (sessions reset on restart) |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///instance/app.db` |
| `SESSION_COOKIE_SECURE` | Send cookies over HTTPS only (`1` behind HTTPS) | `0` |
| `FLASK_DEBUG` | Debug mode for `run.py` (`1` to enable) | `0` |
| `HOST` / `PORT` | Bind address | `127.0.0.1` / `5000` |

Always set a fixed `SECRET_KEY` for anything beyond local development, and never run with `FLASK_DEBUG=1` in production.

## Security measures

- Passwords hashed with Werkzeug (salted); plain text is never stored or logged
- CSRF protection on every form and state-changing request (Flask-WTF); logout, delete and complete are POST-only
- SQL injection prevented by SQLAlchemy ORM with bound parameters; search wildcards are escaped and filter values are whitelisted
- Server-side validation and cleaning of all input; Jinja auto-escaping prevents stored XSS
- Per-user data isolation: every task lookup checks ownership, and another user's task returns `404` so its existence is not revealed
- Generic login error and equalised timing to avoid account enumeration; open-redirect protection on `next`
- Hardened sessions (`HttpOnly`, `SameSite=Lax`, optional `Secure`, 2-hour lifetime, `strong` session protection)
- Security headers: Content-Security-Policy, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`
- No inline scripts or styles, so the CSP stays strict; error pages never expose stack traces

## Notes

- Bootstrap and Font Awesome load from public CDNs (allowed in the CSP). For fully offline or air-gapped
  environments, vendor those files into `app/static/` and adjust the CSP in `app/__init__.py`.
- `requirements.txt` uses pinned versions so dependency scanners give reproducible results. Update the pins
  as new releases and advisories appear.
- Application source lives in `app/`, so analysis tools can target that directory.
