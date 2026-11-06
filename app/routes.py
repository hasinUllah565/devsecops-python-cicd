
"""Main blueprint: landing page, dashboard and task management."""

from datetime import date

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import func

from app import db
from app.auth import is_safe_url
from app.forms import TaskForm
from app.models import (
    PRIORITY_LABELS,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_LABELS,
    STATUS_PENDING,
    TASK_PRIORITIES,
    TASK_STATUSES,
    Task,
)


main_bp = Blueprint("main", __name__)

# Application constants
DEFAULT_TASK_ENDPOINT = "main.tasks"
TASKS_PER_PAGE = 8

SORT_OPTIONS = {
    "newest": "Newest first",
    "oldest": "Oldest first",
    "due": "Deadline",
    "priority": "Priority",
}


def get_owned_task_or_404(task_id: int) -> Task:
    """Return a task only if it belongs to the current user."""

    task = db.session.get(Task, task_id)

    if task is None or task.user_id != current_user.id:
        abort(404)

    return task


def _escape_like(term: str) -> str:
    """Escape LIKE wildcards so searches are matched literally."""

    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _redirect_back(default_endpoint: str = DEFAULT_TASK_ENDPOINT):
    """Redirect to a safe local URL or the default endpoint."""

    next_url = request.form.get("next")

    if is_safe_url(next_url):
        return redirect(next_url)

    return redirect(url_for(default_endpoint))


@main_bp.route("/")
def index():
    """Display the landing page."""

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Display dashboard statistics and recent tasks."""

    user_id = current_user.id
    today = date.today()

    status_rows = db.session.execute(
        db.select(Task.status, func.count(Task.id))
        .where(Task.user_id == user_id)
        .group_by(Task.status)
    ).all()

    by_status = {
        status: count for status, count in status_rows
    }

    total = sum(by_status.values())
    completed = by_status.get(STATUS_COMPLETED, 0)

    priority_rows = db.session.execute(
        db.select(Task.priority, func.count(Task.id))
        .where(
            Task.user_id == user_id,
            Task.status != STATUS_COMPLETED,
        )
        .group_by(Task.priority)
    ).all()

    by_priority = {
        priority: count for priority, count in priority_rows
    }

    stats = {
        "total": total,
        "completed": completed,
        "pending": by_status.get(STATUS_PENDING, 0),
        "in_progress": by_status.get(STATUS_IN_PROGRESS, 0),
        "percent": round(completed / total * 100) if total else 0,
        "overdue": db.session.scalar(
            db.select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.status != STATUS_COMPLETED,
                Task.due_date < today,
            )
        ),
    }

    recent = db.session.scalars(
        db.select(Task)
        .where(Task.user_id == user_id)
        .order_by(
            Task.created_at.desc(),
            Task.id.desc(),
        )
        .limit(5)
    ).all()

    upcoming = db.session.scalars(
        db.select(Task)
        .where(
            Task.user_id == user_id,
            Task.status != STATUS_COMPLETED,
            Task.due_date >= today,
        )
        .order_by(Task.due_date.asc())
        .limit(4)
    ).all()

    return render_template(
        "dashboard.html",
        stats=stats,
        by_priority={
            priority: by_priority.get(priority, 0)
            for priority in TASK_PRIORITIES
        },
        recent=recent,
        upcoming=upcoming,
    )


@main_bp.route("/tasks")
@login_required
def tasks():
    """Display tasks with filtering, searching, sorting and pagination."""

    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    sort = request.args.get("sort", "newest")
    search = (request.args.get("q", "") or "").strip()[:100]
    page = max(request.args.get("page", 1, type=int) or 1, 1)

    # Validate all filter values against allowed options.
    status = status if status in TASK_STATUSES else ""
    priority = priority if priority in TASK_PRIORITIES else ""
    sort = sort if sort in SORT_OPTIONS else "newest"

    query = db.select(Task).where(
        Task.user_id == current_user.id
    )

    if status:
        query = query.where(Task.status == status)

    if priority:
        query = query.where(Task.priority == priority)

    if search:
        pattern = f"%{_escape_like(search)}%"

        query = query.where(
            Task.title.ilike(pattern, escape="\\")
            | Task.description.ilike(pattern, escape="\\")
        )

    # Apply the selected sorting option.
    if sort == "oldest":
        query = query.order_by(
            Task.created_at.asc(),
            Task.id.asc(),
        )

    elif sort == "due":
        query = query.order_by(
            Task.due_date.is_(None),
            Task.due_date.asc(),
            Task.id.desc(),
        )

    elif sort == "priority":
        rank = db.case(
            {
                "high": 0,
                "medium": 1,
                "low": 2,
            },
            value=Task.priority,
            else_=3,
        )

        query = query.order_by(
            rank,
            Task.id.desc(),
        )

    else:
        query = query.order_by(
            Task.created_at.desc(),
            Task.id.desc(),
        )

    pagination = db.paginate(
        query,
        page=page,
        per_page=TASKS_PER_PAGE,
        error_out=False,
    )

    return render_template(
        "tasks.html",
        pagination=pagination,
        tasks=pagination.items,
        filters={
            "status": status,
            "priority": priority,
            "q": search,
            "sort": sort,
        },
        status_labels=STATUS_LABELS,
        priority_labels=PRIORITY_LABELS,
        sort_options=SORT_OPTIONS,
    )


@main_bp.route("/tasks/new", methods=["GET", "POST"])
@login_required
def create_task():
    """Create a new task."""

    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data or "",
            priority=form.priority.data,
            due_date=form.due_date.data,
            user_id=current_user.id,
        )

        task.set_status(form.status.data)

        db.session.add(task)
        db.session.commit()

        flash("Task created.", "success")

        return redirect(url_for(DEFAULT_TASK_ENDPOINT))

    return render_template(
        "task_form.html",
        form=form,
        task=None,
    )


@main_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    """Edit an existing task."""

    task = get_owned_task_or_404(task_id)
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data or ""
        task.priority = form.priority.data
        task.due_date = form.due_date.data

        if form.status.data != task.status:
            task.set_status(form.status.data)

        db.session.commit()

        flash("Task updated.", "success")

        return redirect(url_for(DEFAULT_TASK_ENDPOINT))

    return render_template(
        "task_form.html",
        form=form,
        task=task,
    )


@main_bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def complete_task(task_id):
    """Mark a task as completed."""

    task = get_owned_task_or_404(task_id)

    task.set_status(STATUS_COMPLETED)
    db.session.commit()

    flash("Task marked as completed.", "success")

    return _redirect_back()


@main_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    """Delete an existing task."""

    task = get_owned_task_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    flash("Task deleted.", "info")

    return _redirect_back()

