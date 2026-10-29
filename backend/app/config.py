import os

APP_NAME = os.getenv("APP_NAME", "Task Tracker API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1").rstrip("/")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://taskuser:taskpass@db:5432/taskdb")
