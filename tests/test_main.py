import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from main import Base, app, get_db


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_root_returns_health_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API de tareas funcionando"}


def test_create_and_list_tasks():
    payload = {
        "title": "Estudiar FastAPI",
        "description": "Practicar endpoints CRUD",
        "status": "pendiente",
        "date": "2026-04-27",
    }

    create_response = client.post("/tasks", json=payload)
    list_response = client.get("/tasks")

    assert create_response.status_code == 201
    assert create_response.json()["title"] == payload["title"]
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_get_task_details():
    create_response = client.post("/tasks", json={"title": "Leer docs"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Leer docs"


def test_update_task():
    create_response = client.post("/tasks", json={"title": "Tarea inicial"})
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Tarea actualizada", "status": "completada"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Tarea actualizada"
    assert response.json()["status"] == "completada"


def test_delete_task():
    create_response = client.post("/tasks", json={"title": "Tarea para eliminar"})
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    detail_response = client.get(f"/tasks/{task_id}")

    assert delete_response.status_code == 204
    assert detail_response.status_code == 404
