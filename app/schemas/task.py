"""Task schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "status": "pending"
            }
        }


class TaskRead(BaseModel):
    """Schema for reading task data."""
    
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "status": "pending",
                "created_at": "2026-01-05T10:00:00",
                "updated_at": "2026-01-05T10:00:00"
            }
        }


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    status: Optional[TaskStatus] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated task title",
                "status": "in_progress"
            }
        }


class TaskStatusUpdate(BaseModel):
    """Schema for updating only task status."""
    
    status: TaskStatus = Field(..., description="New task status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "done"
            }
        }
