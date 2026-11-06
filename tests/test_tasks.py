"""Tests for task CRUD, filtering, dashboard statistics and ownership."""
from datetime import date, timedelta

from app import db
from app.models import Task


def task_payload(**overrides):
    data = {
        "title": "Prepare release notes",
        "description": "Summarise the sprint changes",
        "priority": "high",
        "status": "pending",
        "due_date": (date.today() + timedelta(days=7)).isoformat(),
    }
    data.update(overrides)
    return data


def count_tasks():
    return db.session.scalar(db.select(db.func.count(Task.id)))


class TestCreateTask:
    def test_create_task(self, client, alice):
        response = client.post("/tasks/new", data=task_payload())

        assert response.status_code == 302
        task = db.session.scalar(db.select(Task))
        assert task.title == "Prepare release notes"
        assert task.priority == "high"
        assert task.user_id == alice.id
        assert task.due_date == date.today() + timedelta(days=7)

    def test_create_task_without_optional_fields(self, client, alice):
        response = client.post(
            "/tasks/new", data={"title": "Minimal task", "priority": "low", "status": "pending"}
        )

        assert response.status_code == 302
        assert db.session.scalar(db.select(Task)).due_date is None

    def test_short_title_is_rejected(self, client, alice):
        response = client.post("/tasks/new", data=task_payload(title="ab"))

        assert response.status_code == 200
        assert count_tasks() == 0

    def test_invalid_priority_is_rejected(self, client, alice):
        response = client.post("/tasks/new", data=task_payload(priority="urgent"))

        assert response.status_code == 200
        assert count_tasks() == 0

    def test_invalid_date_is_rejected(self, client, alice):
        response = client.post("/tasks/new", data=task_payload(due_date="31/12/2030"))

        assert response.status_code == 200
        assert count_tasks() == 0

    def test_html_in_title_is_escaped_when_rendered(self, client, alice):
        client.post("/tasks/new", data=task_payload(title="<script>alert(1)</script>"))
        response = client.get("/tasks")

        assert b"<script>alert(1)</script>" not in response.data
        assert b"&lt;script&gt;" in response.data


class TestViewTasks:
    def test_user_sees_only_own_tasks(self, client, alice, bob_client, make_task):
        _, bob = bob_client
        make_task(alice, "Alice's private task")
        make_task(bob, "Bob's private task")

        response = client.get("/tasks")

        assert b"Alice&#39;s private task" in response.data
        assert b"Bob&#39;s private task" not in response.data

    def test_filter_by_status(self, client, alice, make_task):
        make_task(alice, "Waiting task", status="pending")
        make_task(alice, "Finished task", status="completed")

        response = client.get("/tasks", query_string={"status": "completed"})

        assert b"Finished task" in response.data
        assert b"Waiting task" not in response.data

    def test_filter_by_priority(self, client, alice, make_task):
        make_task(alice, "Urgent thing", priority="high")
        make_task(alice, "Relaxed thing", priority="low")

        response = client.get("/tasks", query_string={"priority": "high"})

        assert b"Urgent thing" in response.data
        assert b"Relaxed thing" not in response.data

    def test_search_matches_title_and_description(self, client, alice, make_task):
        make_task(alice, "Deploy service", description="rollout to staging")
        make_task(alice, "Buy coffee")

        by_title = client.get("/tasks", query_string={"q": "deploy"})
        by_description = client.get("/tasks", query_string={"q": "STAGING"})

        assert b"Deploy service" in by_title.data and b"Buy coffee" not in by_title.data
        assert b"Deploy service" in by_description.data

    def test_search_treats_wildcards_literally(self, client, alice, make_task):
        make_task(alice, "Plain task")
        make_task(alice, "100% done")

        response = client.get("/tasks", query_string={"q": "%"})

        assert b"100% done" in response.data
        assert b"Plain task" not in response.data

    def test_unknown_filter_values_are_ignored(self, client, alice, make_task):
        make_task(alice, "Still visible")

        response = client.get(
            "/tasks", query_string={"status": "hacked", "priority": "x' OR 1=1 --", "sort": "bad"}
        )

        assert response.status_code == 200
        assert b"Still visible" in response.data

    def test_pagination(self, client, alice, make_task):
        for index in range(10):
            make_task(alice, f"Task number {index:02d}")

        first = client.get("/tasks")
        second = client.get("/tasks", query_string={"page": 2})

        assert first.status_code == 200 and second.status_code == 200
        assert b"Task number 09" in first.data
        assert b"Task number 00" in second.data


class TestUpdateTask:
    def test_edit_page_prefills_values(self, client, alice, make_task):
        task = make_task(alice, "Original title")

        response = client.get(f"/tasks/{task.id}/edit")

        assert response.status_code == 200
        assert b"Original title" in response.data

    def test_update_task(self, client, alice, make_task):
        task = make_task(alice, "Old title", priority="low")

        response = client.post(
            f"/tasks/{task.id}/edit",
            data=task_payload(title="New title", priority="high", status="in_progress"),
        )

        assert response.status_code == 302
        db.session.expire_all()
        updated = db.session.get(Task, task.id)
        assert updated.title == "New title"
        assert updated.priority == "high"
        assert updated.status == "in_progress"

    def test_mark_task_completed(self, client, alice, make_task):
        task = make_task(alice)

        response = client.post(f"/tasks/{task.id}/complete")

        assert response.status_code == 302
        db.session.expire_all()
        done = db.session.get(Task, task.id)
        assert done.status == "completed"
        assert done.completed_at is not None

    def test_reopening_clears_completion_time(self, client, alice, make_task):
        task = make_task(alice, status="completed")

        client.post(f"/tasks/{task.id}/edit", data=task_payload(status="pending"))

        db.session.expire_all()
        assert db.session.get(Task, task.id).completed_at is None

    def test_complete_redirect_ignores_external_next(self, client, alice, make_task):
        task = make_task(alice)

        response = client.post(
            f"/tasks/{task.id}/complete", data={"next": "https://evil.example"}
        )

        assert "evil.example" not in response.headers["Location"]


class TestDeleteTask:
    def test_delete_task(self, client, alice, make_task):
        task = make_task(alice)

        response = client.post(f"/tasks/{task.id}/delete")

        assert response.status_code == 302
        assert count_tasks() == 0

    def test_delete_requires_post(self, client, alice, make_task):
        task = make_task(alice)

        assert client.get(f"/tasks/{task.id}/delete").status_code == 405
        assert count_tasks() == 1


class TestOwnershipAndAuthorization:
    def test_cannot_view_edit_page_of_another_users_task(self, client, alice, bob_client, make_task):
        _, bob = bob_client
        task = make_task(bob, "Bob only")

        assert client.get(f"/tasks/{task.id}/edit").status_code == 404

    def test_cannot_update_another_users_task(self, client, alice, bob_client, make_task):
        _, bob = bob_client
        task = make_task(bob, "Bob only")

        response = client.post(f"/tasks/{task.id}/edit", data=task_payload(title="Hijacked"))

        assert response.status_code == 404
        db.session.expire_all()
        assert db.session.get(Task, task.id).title == "Bob only"

    def test_cannot_delete_another_users_task(self, client, alice, bob_client, make_task):
        _, bob = bob_client
        task = make_task(bob)

        assert client.post(f"/tasks/{task.id}/delete").status_code == 404
        assert count_tasks() == 1

    def test_cannot_complete_another_users_task(self, client, alice, bob_client, make_task):
        _, bob = bob_client
        task = make_task(bob)

        assert client.post(f"/tasks/{task.id}/complete").status_code == 404
        db.session.expire_all()
        assert db.session.get(Task, task.id).status == "pending"

    def test_missing_task_returns_404(self, client, alice):
        assert client.get("/tasks/9999/edit").status_code == 404


class TestDashboard:
    def test_empty_dashboard(self, client, alice):
        response = client.get("/dashboard")

        assert response.status_code == 200
        assert b"No tasks yet" in response.data

    def test_statistics_reflect_own_tasks_only(self, client, alice, bob_client, make_task):
        _, bob = bob_client
        make_task(alice, "A1", status="completed")
        make_task(alice, "A2", status="pending")
        make_task(alice, "A3", status="in_progress")
        make_task(alice, "A4", status="completed")
        make_task(bob, "BobSecretTask", status="completed")

        response = client.get("/dashboard")
        html = response.data.decode()

        assert response.status_code == 200
        assert "2 of 4 tasks completed" in html
        assert "50%" in html
        assert "BobSecretTask" not in html

    def test_overdue_tasks_are_counted(self, client, alice, make_task):
        make_task(alice, "Late", due_date=date.today() - timedelta(days=2))
        make_task(alice, "Late but done", status="completed", due_date=date.today() - timedelta(days=2))

        response = client.get("/dashboard")

        assert b"1 overdue" in response.data
