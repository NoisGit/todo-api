import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient

from main import app, Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_task_success():
    response = client.post(
        "/tasks",
        json={
            "title": "Tarea de prueba",
            "description": "Descripción",
            "status": "pendiente",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Tarea de prueba"
    assert data["status"] == "pendiente"
    assert "date" in data


def test_create_task_without_title_fails():
    response = client.post(
        "/tasks",
        json={
            "description": "Sin título",
            "status": "pendiente",
        },
    )
    assert response.status_code == 422


def test_list_tasks():
    client.post("/tasks", json={"title": "Tarea 1", "status": "pendiente"})
    client.post("/tasks", json={"title": "Tarea 2", "status": "pendiente"})

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
        json={"title": "Detalle", "description": "Algo", "status": "pendiente"},
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
        json={"title": "Viejo título", "description": "Desc", "status": "pendiente"},
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
        json={"title": "Algo", "description": "Desc", "status": "pendiente"},
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
        json={"title": "Para borrar", "description": "Desc", "status": "pendiente"},
    )
    task_id = create_resp.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404


def test_delete_task_not_found():
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
