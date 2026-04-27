# To-Do API

A simple REST API for task management, built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

This project is a small backend practice app focused on CRUD endpoints, request validation, local database persistence, and automated checks through GitHub Actions.

## Features

- Create tasks.
- List all tasks.
- Get task details by ID.
- Update existing tasks.
- Delete tasks.
- Validate request data with Pydantic.
- Store data locally with SQLite.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- HTTPX

## Installation

Clone the repository:

```bash
git clone https://github.com/NoisGit/todo-api.git
cd todo-api
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project

```bash
uvicorn main:app --reload
```

Then open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Main Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/` | Checks that the API is running. |
| GET | `/tasks` | Lists all tasks. |
| POST | `/tasks` | Creates a new task. |
| GET | `/tasks/{details_id}` | Gets task details. |
| PUT | `/tasks/{update_id}` | Updates a task. |
| DELETE | `/tasks/{delete_id}` | Deletes a task. |

## Run Tests

```bash
pytest
```

## Task Example

```json
{
  "title": "Study FastAPI",
  "description": "Practice CRUD endpoints and automated tests",
  "status": "pendiente",
  "date": "2026-04-27"
}
```

> Note: task status values currently use the existing API values: `pendiente` and `completada`.

## Roadmap

- Split the project into modules (`routers`, `schemas`, `models`, `database`).
- Add authentication.
- Add filters by status and date.
- Add Docker support.
- Add environment-based configuration.
- Prepare deployment setup.

## Author

Developed by [NoisGit](https://github.com/NoisGit).
