# Task Tracker API reference

Base URL: `http://localhost:8000`

Interactive OpenAPI documentation: [Swagger UI](http://localhost:8000/docs)  
Alternative OpenAPI UI: [ReDoc](http://localhost:8000/redoc)  
OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

All task endpoints use the `/api/v1` prefix and JSON request/response bodies, except `DELETE`, which returns an empty `204 No Content` response.

## Task resource

| Field         | Type             | Description                        |
| ------------- | ---------------- | ---------------------------------- |
| `id`          | integer          | Database-generated unique ID       |
| `title`       | string           | Required; 1–150 characters         |
| `description` | string or `null` | Optional; maximum 2,000 characters |
| `status`      | string           | `todo`, `in_progress`, or `done`   |
| `created_at`  | date-time        | Creation timestamp (UTC)           |
| `updated_at`  | date-time        | Last update timestamp (UTC)        |

Example task:

```json
{
  "id": 1,
  "title": "Prepare project demo",
  "description": "Finish the demo and verify the API.",
  "status": "todo",
  "created_at": "2026-10-22T07:00:00Z",
  "updated_at": "2026-10-22T07:00:00Z"
}
```

## Endpoints

### `GET /` — API welcome

Returns the API name, version, and convenient paths to the interactive docs and health endpoint (`200 OK`).

Example response:

```json
{
  "name": "Task Tracker API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### `GET /health` — health check

Returns `200 OK` when the API can execute a database query.

Example response:

```json
{ "status": "ok", "database": "ok" }
```

### `GET /api/v1/tasks` — list tasks

Returns an array ordered by ID. Supports filtering and pagination:

| Query    |   Default | Constraints                   |
| -------- | --------: | ----------------------------- |
| `status` | no filter | `todo`, `in_progress`, `done` |
| `limit`  |     `100` | 1–100                         |
| `offset` |       `0` | 0 or greater                  |

Example: `GET /api/v1/tasks?status=todo&limit=20&offset=0` → `200 OK` and a JSON array.

### `GET /api/v1/tasks/{task_id}` — get by ID

Returns the task with that ID (`200 OK`). If it does not exist, returns `404 Not Found` with `{"detail":"Task not found"}`.

Example: `GET /api/v1/tasks/1`.

### `POST /api/v1/tasks` — create

Success: `201 Created`; response includes the generated ID and timestamps.

Request body:

```json
{
  "title": "Prepare project demo",
  "description": "Finish the demo and verify the API.",
  "status": "todo"
}
```

`title` is required. `description` and `status` are optional; their defaults are `null` and `todo`.

### `PUT /api/v1/tasks/{task_id}` — replace/update

Replaces all editable task fields.
Success: `200 OK`; missing ID: `404 Not Found`.

```json
{
  "title": "Prepare final project demo",
  "description": "Demo the complete containerized app.",
  "status": "in_progress"
}
```

### `DELETE /api/v1/tasks/{task_id}` — delete

Success: `204 No Content` with an empty body. Missing ID: `404 Not Found`.

## Common errors

- `404 Not Found`: requested task ID does not exist.
- `422 Unprocessable Entity`: malformed JSON, missing required fields, field length violations, invalid status, or invalid pagination parameters.
- `500 Internal Server Error`: unexpected server/database error; check `docker compose logs backend`.

Validation error responses use FastAPI's standard JSON `detail` structure.
