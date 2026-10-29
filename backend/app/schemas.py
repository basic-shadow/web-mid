from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150,
                       examples=["Prepare project demo"])
    description: str | None = Field(default=None, max_length=2000, examples=[
                                    "Finish the demo and verify the API."])
    status: TaskStatus = "todo"


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def reject_null_for_required_database_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("This field cannot be null when provided")
        return value


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
