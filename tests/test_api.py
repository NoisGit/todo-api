from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path):
    database_url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register(client: TestClient, email: str = "javi@example.com") -> dict:
    response = client.post("/auth/register", json={"email": email, "password": "supersecret"})
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_task(client: TestClient, token: str, **overrides) -> dict:
    payload = {
        "title": "Study FastAPI",
        "description": "Practice real portfolio endpoints",
        "priority": "medium",
        "status": "pendiente",
        "date": str(date.today()),
    }
    payload.update(overrides)
    response = client.post("/tasks", json=payload, headers=auth_headers(token))
    assert response.status_code == 201
    return response.json()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_refresh_logout_flow(client):
    registered = register(client)

    login_response = client.post(
        "/auth/login",
        json={"email": "javi@example.com", "password": "supersecret"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": registered["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": registered["refresh_token"]},
    )
    assert logout_response.status_code == 204

    rejected_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": registered["refresh_token"]},
    )
    assert rejected_refresh.status_code == 401


def test_tasks_are_private_by_user(client):
    user_one = register(client, "one@example.com")
    user_two = register(client, "two@example.com")

    create_task(client, user_one["access_token"], title="Private task")

    response = client.get("/tasks", headers=auth_headers(user_two["access_token"]))

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_task_filters_pagination_sorting_and_search(client):
    token = register(client)["access_token"]
    today = date.today()
    create_task(client, token, title="Alpha task", priority="high", due_date=str(today + timedelta(days=2)))
    create_task(client, token, title="Beta task", priority="low", due_date=str(today - timedelta(days=1)))
    create_task(client, token, title="Gamma note", status="completada", priority="medium")

    search_response = client.get("/tasks?search=Alpha", headers=auth_headers(token))
    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1

    priority_response = client.get("/tasks?priority=low", headers=auth_headers(token))
    assert priority_response.status_code == 200
    assert priority_response.json()["items"][0]["title"] == "Beta task"

    overdue_response = client.get("/tasks?due=overdue", headers=auth_headers(token))
    assert overdue_response.status_code == 200
    assert overdue_response.json()["total"] == 1

    paginated_response = client.get("/tasks?limit=2&offset=1&sort_by=title&sort_order=asc", headers=auth_headers(token))
    assert paginated_response.status_code == 200
    assert paginated_response.json()["limit"] == 2
    assert len(paginated_response.json()["items"]) == 2


def test_complete_soft_delete_restore_stats_and_history(client):
    token = register(client)["access_token"]
    task = create_task(client, token, title="Finish project")

    complete_response = client.patch(f"/tasks/{task['id']}/complete", headers=auth_headers(token))
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completada"

    stats_response = client.get("/tasks/stats", headers=auth_headers(token))
    assert stats_response.status_code == 200
    assert stats_response.json()["completed"] == 1

    delete_response = client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))
    assert delete_response.status_code == 204

    hidden_response = client.get("/tasks", headers=auth_headers(token))
    assert hidden_response.json()["total"] == 0

    deleted_response = client.get("/tasks?deleted_only=true", headers=auth_headers(token))
    assert deleted_response.json()["total"] == 1

    restore_response = client.patch(f"/tasks/{task['id']}/restore", headers=auth_headers(token))
    assert restore_response.status_code == 200
    assert restore_response.json()["deleted_at"] is None

    history_response = client.get(f"/tasks/{task['id']}/history", headers=auth_headers(token))
    assert history_response.status_code == 200
    actions = [item["action"] for item in history_response.json()]
    assert "created" in actions
    assert "completed" in actions
    assert "soft_deleted" in actions
    assert "restored" in actions


def test_bulk_actions_return_processed_and_not_found_ids(client):
    token = register(client)["access_token"]
    first = create_task(client, token, title="First bulk task")
    second = create_task(client, token, title="Second bulk task")

    complete_response = client.post(
        "/tasks/bulk/complete",
        json={"task_ids": [first["id"], 9999]},
        headers=auth_headers(token),
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["processed_ids"] == [first["id"]]
    assert complete_response.json()["not_found_ids"] == [9999]

    delete_response = client.post(
        "/tasks/bulk/delete",
        json={"task_ids": [first["id"], second["id"], 8888]},
        headers=auth_headers(token),
    )
    assert delete_response.status_code == 200
    assert set(delete_response.json()["processed_ids"]) == {first["id"], second["id"]}
    assert delete_response.json()["not_found_ids"] == [8888]


def test_validation_rejects_blank_title(client):
    token = register(client)["access_token"]
    response = client.post(
        "/tasks",
        json={"title": "   ", "description": "Invalid"},
        headers=auth_headers(token),
    )

    assert response.status_code == 422
