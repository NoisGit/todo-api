# To-Do API

![Tests](https://github.com/NoisGit/todo-api/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Portfolio%20API-009688)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

A portfolio-ready REST API for task management, built with **FastAPI**, **SQLAlchemy**, **SQLite**, JWT-style authentication, ownership rules, filtering, soft delete, bulk actions, audit history and deployment-ready configuration.

## Features

- Health check endpoint.
- User registration and login.
- Access token authentication.
- Refresh token flow.
- Logout with refresh token invalidation.
- Task ownership by authenticated user.
- Create, list, detail, update and delete tasks.
- Soft delete and task restore.
- Complete task endpoint.
- Bulk complete and bulk delete endpoints.
- Search by title or description.
- Filters by status, date, priority and due status.
- Pagination with `limit` and `offset`.
- Sorting by `id`, `date`, `title`, `status`, `priority` and `due_date`.
- Task priority: `low`, `medium`, `high`.
- Due dates with overdue and due soon filters.
- Task statistics endpoint for dashboard cards.
- Task audit history for changes and important actions.
- Environment-based configuration.
- Docker support.
- Render deployment blueprint.
- API examples in `docs/api-examples.md`.
- Automated tests with Pytest and GitHub Actions.

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- HTTPX
- Docker
- GitHub Actions

## Project Structure

```text
app/
├── auth.py
├── audit.py
├── config.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── security.py
└── tasks.py

tests/
└── test_api.py

docs/
└── api-examples.md
```

## Installation

```bash
git clone https://github.com/NoisGit/todo-api.git
cd todo-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
venv\Scripts\activate
```

## Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Main variables:

```text
DATABASE_URL=sqlite:///./tasks.db
JWT_SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Run the API

```bash
uvicorn main:app --reload
```

Open the docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

## Authentication Flow

1. Register with `POST /auth/register`.
2. Login with `POST /auth/login`.
3. Copy the `access_token`.
4. Use it in protected endpoints:

```text
Authorization: Bearer <access_token>
```

## Main Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/` | API root. |
| GET | `/health` | Health check. |
| POST | `/auth/register` | Register user. |
| POST | `/auth/login` | Login user. |
| POST | `/auth/refresh` | Refresh access token. |
| POST | `/auth/logout` | Logout user. |
| GET | `/auth/me` | Current user. |
| GET | `/tasks` | List authenticated user's tasks. |
| POST | `/tasks` | Create task. |
| GET | `/tasks/{task_id}` | Get task details. |
| PUT | `/tasks/{task_id}` | Update task. |
| PATCH | `/tasks/{task_id}/complete` | Complete task. |
| DELETE | `/tasks/{task_id}` | Soft delete task. |
| PATCH | `/tasks/{task_id}/restore` | Restore deleted task. |
| GET | `/tasks/stats` | Task statistics. |
| GET | `/tasks/{task_id}/history` | Task audit history. |
| POST | `/tasks/bulk/complete` | Complete many tasks. |
| POST | `/tasks/bulk/delete` | Soft delete many tasks. |

## List Query Parameters

```text
GET /tasks?search=api&status=pendiente&priority=high&limit=10&offset=0&sort_by=due_date&sort_order=asc
```

Supported filters:

- `search`
- `status=pendiente|completada`
- `date=YYYY-MM-DD`
- `priority=low|medium|high`
- `due=overdue|soon`
- `include_deleted=true`
- `deleted_only=true`
- `limit`
- `offset`
- `sort_by=id|date|title|status|priority|due_date`
- `sort_order=asc|desc`

## Request Examples

See:

```text
docs/api-examples.md
```

## Run Tests

```bash
pytest
```

## Docker

```bash
docker build -t todo-api .
docker run -p 8000:8000 --env-file .env todo-api
```

## Deploy

This repository includes `render.yaml` for Render Blueprint deployments.

Recommended production command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

After deploy, the public docs should be available at:

```text
https://your-service-url/docs
```

## Git Flow

```text
feature/* -> develop -> main
```

See `CONTRIBUTING.md` for the workflow.

## Author

Developed by [NoisGit](https://github.com/NoisGit).
