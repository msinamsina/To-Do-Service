"""Task service layer for business logic."""

from datetime import datetime
from typing import Optional
from sqlmodel import Session, select

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service class for task operations."""
    
    def __init__(self, session: Session):
        """Initialize service with database session."""
        self.session = session
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> list[Task]:
        """
        Get all tasks, optionally filtered by status.
        
        Args:
            status: Optional filter by task status
            
        Returns:
            List of tasks
        """
        statement = select(Task)
        if status:
            statement = statement.where(Task.status == status)
        statement = statement.order_by(Task.created_at.desc())
        
        results = self.session.exec(statement)
        return list(results.all())
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get a single task by ID.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task if found, None otherwise
        """
        statement = select(Task).where(Task.id == task_id)
        result = self.session.exec(statement)
        return result.first()
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """
        Create a new task.
        
        Args:
            task_data: Task creation data
            
        Returns:
            Created task
        """
        now = datetime.utcnow()
        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            created_at=now,
            updated_at=now,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """
        Update an existing task.
        
        Args:
            task_id: The task ID
            task_data: Task update data
            
        Returns:
            Updated task if found, None otherwise
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        # Update fields that are provided
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        # Always update updated_at timestamp
        task.updated_at = datetime.utcnow()
        
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def update_task_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        """
        Update only the status of a task.
        
        Args:
            task_id: The task ID
            status: New task status
            
        Returns:
            Updated task if found, None otherwise
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        task.status = status
        task.updated_at = datetime.utcnow()
        
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: The task ID
            
        Returns:
            True if deleted, False if not found
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        self.session.delete(task)
        self.session.commit()
        return True
