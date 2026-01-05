"""FastMCP Server for Todo Service."""

from contextlib import asynccontextmanager
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from pydantic import Field

from app.db.session import get_sync_session, init_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


# Initialize the FastMCP server
mcp = FastMCP("todo-fastmcp-server")


# Context manager to initialize database
@asynccontextmanager
async def lifespan():
    """Initialize database on startup."""
    init_db()
    yield


def get_service() -> TaskService:
    """Get a task service with a fresh session."""
    session = get_sync_session()
    return TaskService(session)


def format_task(task) -> dict:
    """Format task for JSON output."""
    return task.to_dict()


def validate_status(status_str: str) -> TaskStatus:
    """Validate and convert status string to TaskStatus enum."""
    status_map = {
        "pending": TaskStatus.PENDING,
        "in_progress": TaskStatus.IN_PROGRESS,
        "done": TaskStatus.DONE,
    }
    
    status_lower = status_str.lower()
    if status_lower not in status_map:
        raise ValueError(
            f"Invalid status: {status_str}. Must be one of: pending, in_progress, done"
        )
    return status_map[status_lower]


# ==================== TOOLS ====================

@mcp.tool(
    annotations=ToolAnnotations(
        title="List Tasks",
        description="Retrieve all tasks with optional status filtering",
        audience=["user", "assistant"]
    )
)
def list_tasks(
    status: Optional[str] = Field(
        None,
        description="Filter tasks by status (pending, in_progress, done)"
    )
) -> dict:
    """
    List all tasks. Optionally filter by status.
    
    Returns a dictionary containing a list of tasks with their details.
    """
    service = get_service()
    
    # Validate status if provided
    status_enum = None
    if status:
        try:
            status_enum = validate_status(status)
        except ValueError as e:
            return {"error": str(e)}
    
    tasks = service.get_all_tasks(status=status_enum)
    return {"tasks": [format_task(task) for task in tasks]}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Task by ID",
        description="Retrieve detailed information about a specific task",
        audience=["user", "assistant"]
    )
)
def get_task_by_id(
    task_id: int = Field(..., description="The task ID to retrieve")
) -> dict:
    """
    Get details of a specific task by its ID.
    
    Returns the task details including title, description, status, and timestamps.
    """
    service = get_service()
    task = service.get_task_by_id(task_id)
    
    if not task:
        return {"error": f"Task with id {task_id} not found"}
    
    return {"task": format_task(task)}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Create Task",
        description="Create a new task with title, description, and status",
        audience=["user", "assistant"]
    )
)
def create_task(
    title: str = Field(..., description="The task title (required, max 200 chars)"),
    description: Optional[str] = Field(None, description="The task description"),
    status: str = Field("pending", description="Initial task status (pending, in_progress, done)")
) -> dict:
    """
    Create a new task with a title and optional description and status.
    
    Returns the newly created task with its ID and timestamps.
    """
    # Validate title length
    if len(title) > 200:
        return {"error": "Title must be 200 characters or less"}
    
    # Validate status
    try:
        status_enum = validate_status(status)
    except ValueError as e:
        return {"error": str(e)}
    
    task_data = TaskCreate(
        title=title,
        description=description,
        status=status_enum
    )
    
    service = get_service()
    task = service.create_task(task_data)
    
    return {"task": format_task(task)}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Update Task",
        description="Update task properties including title, description, and status",
        audience=["user", "assistant"]
    )
)
def update_task(
    task_id: int = Field(..., description="The task ID to update"),
    title: Optional[str] = Field(None, description="New task title (max 200 chars)"),
    description: Optional[str] = Field(None, description="New task description"),
    status: Optional[str] = Field(None, description="New task status (pending, in_progress, done)")
) -> dict:
    """
    Update an existing task. Can update title, description, and/or status.
    
    Returns the updated task with new values.
    """
    # Validate title length if provided
    if title and len(title) > 200:
        return {"error": "Title must be 200 characters or less"}
    
    # Validate status if provided
    status_enum = None
    if status:
        try:
            status_enum = validate_status(status)
        except ValueError as e:
            return {"error": str(e)}
    
    # Build update data
    update_dict = {}
    if title is not None:
        update_dict["title"] = title
    if description is not None:
        update_dict["description"] = description
    if status_enum is not None:
        update_dict["status"] = status_enum
    
    if not update_dict:
        return {"error": "No fields to update"}
    
    task_data = TaskUpdate(**update_dict)
    
    service = get_service()
    task = service.update_task(task_id, task_data)
    
    if not task:
        return {"error": f"Task with id {task_id} not found"}
    
    return {"task": format_task(task)}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Update Task Status",
        description="Change the status of a task (pending, in_progress, done)",
        audience=["user", "assistant"]
    )
)
def update_task_status(
    task_id: int = Field(..., description="The task ID"),
    status: str = Field(..., description="The new task status (pending, in_progress, done)")
) -> dict:
    """
    Update the status of an existing task.
    
    Returns the updated task with the new status.
    """
    # Validate status
    try:
        status_enum = validate_status(status)
    except ValueError as e:
        return {"error": str(e)}
    
    service = get_service()
    task = service.update_task_status(task_id, status_enum)
    
    if not task:
        return {"error": f"Task with id {task_id} not found"}
    
    return {"task": format_task(task)}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Delete Task",
        description="Permanently remove a task from the system",
        audience=["user", "assistant"]
    )
)
def delete_task(
    task_id: int = Field(..., description="The task ID to delete")
) -> dict:
    """
    Delete a task by its ID.
    
    Returns confirmation of deletion.
    """
    service = get_service()
    deleted = service.delete_task(task_id)
    
    if not deleted:
        return {"error": f"Task with id {task_id} not found"}
    
    return {"deleted": True, "id": task_id}


# ==================== PROMPTS ====================

@mcp.prompt()
def task_management_guide() -> str:
    """
    A comprehensive guide for managing tasks using this Todo Service.
    """
    return """# Task Management Guide

## Available Operations

### 1. List Tasks
- View all tasks or filter by status (pending, in_progress, done)
- Example: "Show me all pending tasks"

### 2. Get Task Details
- Retrieve detailed information about a specific task by ID
- Example: "Show details for task 5"

### 3. Create Task
- Create a new task with title, description, and status
- Title is required (max 200 characters)
- Status defaults to 'pending' if not specified
- Example: "Create a task titled 'Buy groceries'"

### 4. Update Task
- Modify task title, description, or status
- Can update one or more fields at once
- Example: "Update task 3 to status done"

### 5. Delete Task
- Remove a task by ID
- Example: "Delete task 7"

## Status Values
- **pending**: Task is not yet started
- **in_progress**: Task is currently being worked on
- **done**: Task is completed

## Best Practices
1. Always provide clear, concise task titles
2. Use descriptions to add context and details
3. Update status as work progresses
4. Delete tasks only when no longer needed

## Persian Commands Support
This service supports commands in both English and Persian:
- لیست تسک‌ها (List tasks)
- ایجاد تسک (Create task)
- به‌روزرسانی تسک (Update task)
- حذف تسک (Delete task)
"""


@mcp.prompt()
def task_status_workflow() -> str:
    """
    Describes the typical workflow for task status transitions.
    """
    return """# Task Status Workflow

## Status Lifecycle

```
pending → in_progress → done
   ↑           ↓           ↓
   └───────────────────────┘
```

### 1. Pending (شروع نشده)
- Initial state for new tasks
- Tasks waiting to be started
- Use when: Planning or backlog items

### 2. In Progress (در حال انجام)
- Active work in progress
- Someone is currently working on this
- Use when: Starting work on a task

### 3. Done (انجام شده)
- Task is completed
- No further action needed
- Use when: Work is finished and verified

## Common Transitions

### Starting Work
```
Status: pending → in_progress
Command: update_task_status(task_id=X, status="in_progress")
```

### Completing Work
```
Status: in_progress → done
Command: update_task_status(task_id=X, status="done")
```

### Reopening Task
```
Status: done → pending or in_progress
Command: update_task_status(task_id=X, status="pending")
```

## Tips
- Move tasks to 'in_progress' when you start working
- Update to 'done' only when fully completed
- Review 'done' tasks periodically for archival
"""


@mcp.prompt()
def create_task_template(
    task_title: str = Field(..., description="The title of the task to create")
) -> str:
    """
    Generate a template for creating a well-structured task.
    """
    return f"""# Create Task: {task_title}

## Task Details

**Title**: {task_title}

**Description**: 
[Provide a detailed description of what needs to be done]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Status**: pending

**Estimated Effort**: [Small/Medium/Large]

**Notes**:
- Any additional context or requirements
- Dependencies or blockers
- Resources needed

## Action
To create this task, use:
```
create_task(
    title="{task_title}",
    description="[Fill in description]",
    status="pending"
)
```
"""


@mcp.prompt()
def daily_task_summary() -> str:
    """
    Generate a template for daily task review and planning.
    """
    return """# Daily Task Summary

## Morning Review (صبح)

### Tasks to Complete Today
Use: `list_tasks(status="pending")` to see pending tasks

**Priority Tasks**:
1. [High priority task]
2. [High priority task]
3. [High priority task]

### In Progress Tasks
Use: `list_tasks(status="in_progress")` to see active tasks

**Continue Working On**:
- [Task in progress]
- [Task in progress]

## End of Day Review (پایان روز)

### Completed Today
Use: `list_tasks(status="done")` to see completed tasks

**Achievements** ✅:
- [Completed task]
- [Completed task]

### Carry Over
**Tasks for Tomorrow**:
- [Incomplete task - update status to pending]
- [New task - create if needed]

### Reflection
- What went well today?
- What challenges did you face?
- What can be improved tomorrow?

## Quick Commands
```
# See all tasks
list_tasks()

# Filter by status
list_tasks(status="pending")
list_tasks(status="in_progress")
list_tasks(status="done")

# Update completed tasks
update_task_status(task_id=X, status="done")

# Plan tomorrow's tasks
create_task(title="...", description="...")
```
"""


# Run the server
if __name__ == "__main__":
    # Initialize database
    init_db()
    # Run with mcp dev app/mcp_server/fastmcp_server
    mcp.run()
