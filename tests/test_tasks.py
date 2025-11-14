import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient

from main import app, Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_task_payload(**overrides):
    payload = {
        "title": "Tarea por defecto",
        "description": "Descripción de prueba",
        "status": "pendiente",
    }
    payload.update(overrides)
    return payload


def test_create_task_success():
    response = client.post(
        "/tasks",
        json=make_task_payload(title="Tarea de prueba"),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Tarea de prueba"
    assert data["status"] == "pendiente"
    assert data["description"] == "Descripción de prueba"
    assert "date" in data


def test_create_task_without_title_fails():
    bad_payload = {
        "description": "Sin título",
        "status": "pendiente",
    }
    response = client.post("/tasks", json=bad_payload)
    assert response.status_code == 422


def test_list_tasks_returns_all_items():
    client.post("/tasks", json=make_task_payload(title="Tarea 1"))
    client.post("/tasks", json=make_task_payload(title="Tarea 2"))

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [t["title"] for t in data]
    assert "Tarea 1" in titles
    assert "Tarea 2" in titles


def test_get_task_detail_success():
    create_resp = client.post(
        "/tasks",
        json=make_task_payload(title="Detalle", description="Algo"),
    )
    task_id = create_resp.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Detalle"


def test_get_task_not_found():
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_update_task_success():
    create_resp = client.post(
        "/tasks",
        json=make_task_payload(title="Viejo título", description="Desc"),
    )
    task_id = create_resp.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Nuevo título", "status": "completada"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Nuevo título"
    assert data["status"] == "completada"


def test_update_task_no_fields():
    create_resp = client.post(
        "/tasks",
        json=make_task_payload(title="Algo", description="Desc"),
    )
    task_id = create_resp.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={})
    assert response.status_code == 400


def test_update_task_not_found():
    response = client.put(
        "/tasks/9999",
        json={"title": "No existe", "status": "pendiente"},
    )
    assert response.status_code == 404


def test_delete_task_success():
    create_resp = client.post(
        "/tasks",
        json=make_task_payload(title="Para borrar", description="Desc"),
    )
    task_id = create_resp.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404


def test_delete_task_not_found():
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
