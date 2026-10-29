from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.config import API_PREFIX, APP_NAME, APP_VERSION
from app.database import Base, engine, get_db
from app.models import Task
from app.schemas import TaskCreate, TaskPatch, TaskRead, TaskStatus


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=APP_NAME, version=APP_VERSION, description="A small task-management REST API. Use it to create tasks, track their status, and update or remove them. The interactive OpenAPI reference is available at /docs.",
              lifespan=lifespan, openapi_tags=[{"name": "Tasks", "description": "Create, read, update, and delete tasks."}])
DbSession = Annotated[Session, Depends(get_db)]


def _task_or_404(task_id, db) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/", tags=["System"], summary="API welcome")
def root() -> dict[str, str]: return {"name": APP_NAME,
                                      "version": APP_VERSION, "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["System"], summary="Check API and database health")
def health(db) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@app.get(f"{API_PREFIX}/tasks", response_model=list[TaskRead], tags=["Tasks"], summary="List tasks")
def list_tasks(
    db: DbSession,
    task_status: TaskStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Task]:
    query = select(Task).order_by(Task.id).offset(offset).limit(limit)
    if task_status is not None:
        query = query.where(Task.status == task_status)
    return list(db.scalars(query).all())


@app.get(f"{API_PREFIX}/tasks/{{task_id}}", response_model=TaskRead, tags=["Tasks"], summary="Get a task by ID", responses={404: {"description": "Task not found"}})
def get_task(task_id, db: DbSession) -> Task: return _task_or_404(task_id, db)


@app.post(f"{API_PREFIX}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["Tasks"], summary="Create a task")
def create_task(payload: TaskCreate, db: DbSession) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.put(f"{API_PREFIX}/tasks/{{task_id}}", response_model=TaskRead, tags=["Tasks"], summary="Update selected task fields", responses={404: {"description": "Task not found"}})
def update_task(task_id, payload: TaskPatch, db: DbSession) -> Task:
    task = _task_or_404(task_id, db)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=422, detail="Provide at least one field to update")
    for field, value in changes.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete(f"{API_PREFIX}/tasks/{{task_id}}", status_code=200, tags=["Tasks"], summary="Delete a task")
def delete_task(task_id: int, db: DbSession) -> dict:
    db.delete(_task_or_404(task_id, db))
    db.commit()
    return {"success": True, "message": "Task deleted successfully"}
