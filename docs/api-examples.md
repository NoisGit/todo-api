# API Request Examples

Base URL for local development:

```text
http://127.0.0.1:8000
```

## Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "javi@example.com",
  "password": "supersecret"
}
```

## Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "javi@example.com",
  "password": "supersecret"
}
```

## Create task

```http
POST /tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Finish portfolio API",
  "description": "Polish endpoints, docs and deployment",
  "status": "pendiente",
  "priority": "high",
  "date": "2026-04-29",
  "due_date": "2026-05-05"
}
```

## List tasks with filters

```http
GET /tasks?search=portfolio&priority=high&limit=10&offset=0&sort_by=due_date&sort_order=asc
Authorization: Bearer <access_token>
```

## Complete task

```http
PATCH /tasks/1/complete
Authorization: Bearer <access_token>
```

## Soft delete task

```http
DELETE /tasks/1
Authorization: Bearer <access_token>
```

## Restore task

```http
PATCH /tasks/1/restore
Authorization: Bearer <access_token>
```

## Bulk complete

```http
POST /tasks/bulk/complete
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "task_ids": [1, 2, 3]
}
```

## Task stats

```http
GET /tasks/stats
Authorization: Bearer <access_token>
```

## Task history

```http
GET /tasks/1/history
Authorization: Bearer <access_token>
```
