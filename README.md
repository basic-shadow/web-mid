# Task Tracker API — Docker Compose project

A small, fully containerized task-management REST API built with **Python, FastAPI, SQLAlchemy, and PostgreSQL**. It lets you create tasks, query and filter them, update progress, and delete tasks. The API is designed for a coursework/demo environment and includes a Postman collection and automated tests.

## Quick start

Requirements: Docker Engine and Docker Compose v2.

```bash
# Optional: customize settings first
cp .env.example .env

# Build the custom backend image and start both services
# `docker compose up` also builds the backend when its image is missing.
docker compose up --build
```

When both containers are healthy, open:

- API base: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health endpoint: <http://localhost:8000/health>

To stop containers, press `Ctrl+C`, then run `docker compose down`. To stop and remove the database volume too, run `docker compose down -v` (this permanently deletes persisted database data).

## Quick API example

Create a task:

```bash
curl -i http://localhost:8000/api/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Prepare project demo","description":"Verify the API","status":"todo"}'
```

List tasks:

```bash
curl 'http://localhost:8000/api/v1/tasks?status=todo&limit=20&offset=0'
```

Get, update, and delete a task (replace `1` with the returned ID):

```bash
curl http://localhost:8000/api/v1/tasks/1
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{"title":"Demo API","description":"Ready for review","status":"in_progress"}'
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H 'Content-Type: application/json' -d '{"status":"done"}'
curl -i -X DELETE http://localhost:8000/api/v1/tasks/1
```

## Postman

Import `postman/Task-Tracker-API.postman_collection.json` into Postman. The collection variable `baseUrl` defaults to `http://localhost:8000`. Run the collection in order: health check, list, create, get, PUT update, PATCH update, delete. The Create request saves the generated ID to `taskId` and later requests use it automatically.

## Automated tests

The tests use an in-memory SQLite database, so they do not need Docker or a PostgreSQL process. With Python 3.12+ installed:

```bash
cd backend
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

## Configuration

Compose reads a `.env` file in the project root if present. See `.env.example`.

| Variable            | Default             | Purpose                                                     |
| ------------------- | ------------------- | ----------------------------------------------------------- |
| `APP_NAME`          | `Task Tracker API`  | API title shown in docs                                     |
| `APP_VERSION`       | `1.0.0`             | API version                                                 |
| `LOG_LEVEL`         | `info`              | Uvicorn log verbosity configuration value                   |
| `API_PREFIX`        | `/api/v1`           | Versioned API route prefix                                  |
| `API_PORT`          | `8000`              | Host port mapped to backend port 8000                       |
| `POSTGRES_DB`       | `taskdb`            | PostgreSQL database name                                    |
| `POSTGRES_USER`     | `taskuser`          | PostgreSQL username                                         |
| `POSTGRES_PASSWORD` | `taskpass_dev_only` | Local development password; change before external exposure |

The backend connects to the database using the Compose service hostname `db` and the internal port `5432`. Do not use `localhost` for the database host from inside the backend container.

## Architecture and infrastructure requirements

- `backend`: custom image built from `backend/Dockerfile`, running the FastAPI app on port 8000 as a non-root user.
- `db`: PostgreSQL 16 Alpine image.
- `task-tracker-network`: user-defined bridge network connecting backend and database by service DNS name.
- `postgres_data`: named volume mounted at PostgreSQL's data directory, preserving data across container replacement/restarts.
- Database health check uses `pg_isready`; the backend waits for the database health check to pass before starting.
- Backend health check calls `/health`, which performs a real database query.
- Compose injects configuration through environment variables. The database URL is constructed by Compose and points to `db:5432`.

## Project tree

```text
task-tracker-api/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
├── docs/API.md
├── postman/Task-Tracker-API.postman_collection.json
├── .env
├── .gitignore
└── compose.yaml
```

## Notes

- Table creation is automatic at application startup for easy local setup. For production deployments, replace `create_all` with a migration tool such as Alembic, use a managed secret for the database password, and add authentication/authorization as needed.
- Do not commit `.env` files containing real credentials.
