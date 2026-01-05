"""Task API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(session: Session = Depends(get_session)) -> TaskService:
    """Dependency to get task service."""
    return TaskService(session)


@router.get("", response_model=list[TaskRead])
def list_tasks(
    status: Optional[TaskStatus] = Query(default=None, description="Filter by status"),
    service: TaskService = Depends(get_task_service),
) -> list[TaskRead]:
    """
    Get list of all tasks.
    
    Optionally filter by status: pending, in_progress, done
    """
    try:
        tasks = service.get_all_tasks(status=status)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching tasks"
        ) from e


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Get a single task by ID."""
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Create a new task."""
    try:
        task = service.create_task(task_data)
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the task"
        ) from e


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Update an existing task."""
    try:
        task = service.update_task(task_id, task_data)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the task"
        ) from e


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Partially update an existing task."""
    return update_task(task_id, task_data, service)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> dict:
    """Delete a task by ID."""
    try:
        deleted = service.delete_task(task_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return {"deleted": True, "id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the task"
        ) from e
