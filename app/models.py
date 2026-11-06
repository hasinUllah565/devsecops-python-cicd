"""Database models: users and their tasks."""
from datetime import date, datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
TASK_STATUSES = (STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED)

PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
TASK_PRIORITIES = (PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH)

STATUS_LABELS = {
    STATUS_PENDING: "Pending",
    STATUS_IN_PROGRESS: "In Progress",
    STATUS_COMPLETED: "Completed",
}
PRIORITY_LABELS = {
    PRIORITY_LOW: "Low",
    PRIORITY_MEDIUM: "Medium",
    PRIORITY_HIGH: "High",
}


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """A registered user. Only a password hash is ever stored."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    tasks = db.relationship(
        "Task", back_populates="owner", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and store the password (never the plain text)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Task(db.Model):
    """A task owned by exactly one user."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    priority = db.Column(db.String(10), nullable=False, default=PRIORITY_MEDIUM, index=True)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    owner = db.relationship("User", back_populates="tasks")

    @property
    def is_completed(self) -> bool:
        return self.status == STATUS_COMPLETED

    @property
    def is_overdue(self) -> bool:
        """True when the deadline has passed and the task is not completed."""
        return (
            self.due_date is not None
            and not self.is_completed
            and self.due_date < date.today()
        )

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def priority_label(self) -> str:
        return PRIORITY_LABELS.get(self.priority, self.priority)

    def set_status(self, status: str) -> None:
        """Change status and keep the completion timestamp consistent."""
        self.status = status
        self.completed_at = utcnow() if status == STATUS_COMPLETED else None

    def __repr__(self) -> str:
        return f"<Task {self.id} {self.title!r}>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login hook: load a user from the session's stored id."""
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
