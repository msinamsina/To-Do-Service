"""MCP Server for Todo Service using the official mcp package."""

import json
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)
from pydantic import BaseModel

from app.db.session import get_sync_session, init_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


# Create MCP Server instance
server = Server("todo-mcp-server")


class MCPError(Exception):
    """Custom MCP error with code and message."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def get_service() -> TaskService:
    """Get a task service with a fresh session."""
    session = get_sync_session()
    return TaskService(session)


def format_error(code: str, message: str) -> dict:
    """Format error response."""
    return {"error": {"code": code, "message": message}}


def format_task(task) -> dict:
    """Format task for JSON output."""
    return task.to_dict()


def validate_status(status_str: str) -> Optional[TaskStatus]:
    """Validate and convert status string to TaskStatus enum."""
    if not status_str:
        return None
    
    status_map = {
        "pending": TaskStatus.PENDING,
        "in_progress": TaskStatus.IN_PROGRESS,
        "done": TaskStatus.DONE,
    }
    
    status_lower = status_str.lower()
    if status_lower not in status_map:
        raise MCPError(
            code="INVALID_STATUS",
            message=f"Invalid status: {status_str}. Must be one of: pending, in_progress, done"
        )
    return status_map[status_lower]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="list_tasks",
            description="List all tasks. Optionally filter by status (pending, in_progress, done).",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "done"],
                        "description": "Filter tasks by status"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_task_by_id",
            description="Get details of a specific task by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The task ID"
                    }
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="create_task",
            description="Create a new task with a title and optional description and status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title (required, max 200 chars)"
                    },
                    "description": {
                        "type": "string",
                        "description": "The task description (optional)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "done"],
                        "description": "Initial task status (default: pending)"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="update_task_status",
            description="Update the status of an existing task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The task ID"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "done"],
                        "description": "The new task status"
                    }
                },
                "required": ["id", "status"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The task ID to delete"
                    }
                },
                "required": ["id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_tasks":
            return await handle_list_tasks(arguments)
        elif name == "get_task_by_id":
            return await handle_get_task_by_id(arguments)
        elif name == "create_task":
            return await handle_create_task(arguments)
        elif name == "update_task_status":
            return await handle_update_task_status(arguments)
        elif name == "delete_task":
            return await handle_delete_task(arguments)
        else:
            result = format_error("UNKNOWN_TOOL", f"Unknown tool: {name}")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except MCPError as e:
        result = format_error(e.code, e.message)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except Exception as e:
        result = format_error("INTERNAL_ERROR", f"An unexpected error occurred: {str(e)}")
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]


async def handle_list_tasks(arguments: dict) -> list[TextContent]:
    """Handle list_tasks tool call."""
    service = get_service()
    status_str = arguments.get("status")
    status = validate_status(status_str) if status_str else None
    
    tasks = service.get_all_tasks(status=status)
    result = {"tasks": [format_task(task) for task in tasks]}
    
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def handle_get_task_by_id(arguments: dict) -> list[TextContent]:
    """Handle get_task_by_id tool call."""
    task_id = arguments.get("id")
    if task_id is None:
        raise MCPError("MISSING_PARAMETER", "Parameter 'id' is required")
    
    service = get_service()
    task = service.get_task_by_id(int(task_id))
    
    if not task:
        raise MCPError("NOT_FOUND", f"Task with id {task_id} not found")
    
    result = {"task": format_task(task)}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def handle_create_task(arguments: dict) -> list[TextContent]:
    """Handle create_task tool call."""
    title = arguments.get("title")
    if not title:
        raise MCPError("MISSING_PARAMETER", "Parameter 'title' is required")
    
    if len(title) > 200:
        raise MCPError("VALIDATION_ERROR", "Title must be 200 characters or less")
    
    description = arguments.get("description")
    status_str = arguments.get("status", "pending")
    status = validate_status(status_str)
    
    task_data = TaskCreate(
        title=title,
        description=description,
        status=status or TaskStatus.PENDING
    )
    
    service = get_service()
    task = service.create_task(task_data)
    
    result = {"task": format_task(task)}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def handle_update_task_status(arguments: dict) -> list[TextContent]:
    """Handle update_task_status tool call."""
    task_id = arguments.get("id")
    if task_id is None:
        raise MCPError("MISSING_PARAMETER", "Parameter 'id' is required")
    
    status_str = arguments.get("status")
    if not status_str:
        raise MCPError("MISSING_PARAMETER", "Parameter 'status' is required")
    
    status = validate_status(status_str)
    
    service = get_service()
    task = service.update_task_status(int(task_id), status)
    
    if not task:
        raise MCPError("NOT_FOUND", f"Task with id {task_id} not found")
    
    result = {"task": format_task(task)}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def handle_delete_task(arguments: dict) -> list[TextContent]:
    """Handle delete_task tool call."""
    task_id = arguments.get("id")
    if task_id is None:
        raise MCPError("MISSING_PARAMETER", "Parameter 'id' is required")
    
    service = get_service()
    deleted = service.delete_task(int(task_id))
    
    if not deleted:
        raise MCPError("NOT_FOUND", f"Task with id {task_id} not found")
    
    result = {"deleted": True, "id": int(task_id)}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def run_server():
    """Run the MCP server."""
    # Initialize database on startup
    init_db()
    
    # Run the stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Main entry point."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
