"""MCP Client CLI for Todo Service using the official mcp package."""

import asyncio
import json
import re
import sys
import os
from typing import Optional, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Persian to English status mapping
STATUS_MAPPING = {
    # Persian terms
    "انجام‌شده": "done",
    "انجام شده": "done",
    "تمام شده": "done",
    "تموم شده": "done",
    "انجام": "done",
    "تمام": "done",
    "در حال انجام": "in_progress",
    "درحال انجام": "in_progress",
    "در جریان": "in_progress",
    "شروع شده": "in_progress",
    "معلق": "pending",
    "در انتظار": "pending",
    "منتظر": "pending",
    # English terms
    "done": "done",
    "completed": "done",
    "finish": "done",
    "finished": "done",
    "in_progress": "in_progress",
    "in progress": "in_progress",
    "inprogress": "in_progress",
    "started": "in_progress",
    "working": "in_progress",
    "pending": "pending",
    "waiting": "pending",
    "new": "pending",
}


def parse_user_input(user_input: str) -> Tuple[Optional[str], dict]:
    """
    Parse user input to determine the tool and arguments.
    
    Returns:
        Tuple of (tool_name, arguments_dict) or (None, {}) if not recognized
    """
    text = user_input.lower().strip()
    
    # Pattern for listing tasks
    list_patterns = [
        r"لیست.*تسک",
        r"تسک.*ها.*نشون",
        r"نشون.*بده.*تسک",
        r"همه.*تسک",
        r"لیست.*(pending|in_progress|done|انجام|معلق)",
        r"(pending|in_progress|done).*لیست",
        r"list.*task",
        r"show.*task",
        r"get.*task",
        r"all.*task",
        r"list.*(pending|in_progress|done)",
        r"(pending|in_progress|done).*list",
    ]
    
    # Pattern for creating tasks
    create_patterns = [
        r"(?:یک\s*)?تسک.*(?:جدید\s*)?(?:با\s*عنوان|عنوان)\s+[\"']?(.+?)[\"']?(?:\s*بساز)?$",
        r"(?:بساز|ایجاد).*تسک.*(?:با\s*عنوان|عنوان)\s+[\"']?(.+?)[\"']?",
        r"(?:تسک\s*)?(?:جدید\s*)?(?:با\s*عنوان|عنوان)\s+[\"']?(.+?)[\"']?\s*(?:بساز|ایجاد)",
        r"create.*task.*(?:titled?|with)\s+[\"']?(.+)[\"']?$",
        r"new.*task\s+[\"']?(.+)[\"']?$",
        r"add.*task\s+[\"']?(.+)[\"']?$",
    ]
    
    # Pattern for updating status
    update_patterns = [
        r"وضعیت.*تسک\s*(\d+).*(?:رو|را)?\s*(pending|in_progress|done|انجام|تمام|معلق)",
        r"(?:تسک\s*)?(\d+).*(?:رو|را)?\s*(pending|in_progress|done|انجام|تمام|معلق)\s*کن",
        r"(?:تغییر|آپدیت).*(?:وضعیت)?.*(\d+).*(?:به)?\s*(pending|in_progress|done|انجام|تمام|معلق)",
        r"update.*(?:task\s*)?(\d+).*(?:to|status)?\s*(pending|in_progress|done)",
        r"(?:mark|set).*(?:task\s*)?(\d+).*(?:as|to)?\s*(pending|in_progress|done)",
    ]
    
    # Pattern for getting task details
    detail_patterns = [
        r"جزئیات.*تسک\s*(\d+)",
        r"تسک\s*(\d+).*(?:جزئیات|نشون|ببین)",
        r"(?:نشون|نمایش).*تسک\s*(\d+)",
        r"(?:get|show|view).*task\s*(\d+)",
        r"task\s*(\d+).*(?:detail|info)",
        r"(?:detail|info).*(?:of|for)?.*task\s*(\d+)",
    ]
    
    # Pattern for deleting tasks
    delete_patterns = [
        r"(?:حذف|پاک).*تسک\s*(\d+)",
        r"تسک\s*(\d+).*(?:رو|را)?\s*(?:حذف|پاک)\s*کن",
        r"delete.*task\s*(\d+)",
        r"remove.*task\s*(\d+)",
        r"task\s*(\d+).*delete",
    ]
    
    # Check for list with status filter
    for pattern in list_patterns:
        if re.search(pattern, text):
            # Check for status filter
            status = None
            # First check for English status in original input
            for eng_status in ["pending", "in_progress", "done"]:
                if eng_status in user_input.lower():
                    status = eng_status
                    break
            # Then check for Persian status
            if not status:
                for persian, english in STATUS_MAPPING.items():
                    if persian in user_input:
                        status = english
                        break
            
            args = {}
            if status:
                args["status"] = status
            return ("list_tasks", args)
    
    # Check for create task
    for pattern in create_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s*(بساز|ایجاد کن|create|add).*$', '', title, flags=re.IGNORECASE)
            title = title.strip().strip('"\'')
            if title:
                return ("create_task", {"title": title})
    
    # Check for update status
    for pattern in update_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            task_id = int(match.group(1))
            status_raw = match.group(2).strip()
            status = STATUS_MAPPING.get(status_raw, status_raw)
            return ("update_task_status", {"id": task_id, "status": status})
    
    # Check for get task details
    for pattern in detail_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            task_id = int(match.group(1))
            return ("get_task_by_id", {"id": task_id})
    
    # Check for delete task
    for pattern in delete_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            task_id = int(match.group(1))
            return ("delete_task", {"id": task_id})
    
    # Fallback: try to extract any number and status for update
    numbers = re.findall(r'\d+', text)
    if numbers:
        task_id = int(numbers[0])
        
        # Check for status words
        for persian, english in STATUS_MAPPING.items():
            if persian in text:
                return ("update_task_status", {"id": task_id, "status": english})
        
        # Just show details if only a number mentioned
        if "جزئیات" in text or "detail" in text or "نشون" in text or "show" in text:
            return ("get_task_by_id", {"id": task_id})
    
    # Check if it's just asking for list
    if any(word in text for word in ["تسک", "task", "list", "لیست", "همه", "all"]):
        return ("list_tasks", {})
    
    return (None, {})


def format_task_table(tasks: list) -> str:
    """Format tasks as a simple table."""
    if not tasks:
        return "هیچ تسکی یافت نشد / No tasks found"
    
    # Header
    lines = [
        "┌" + "─" * 6 + "┬" + "─" * 32 + "┬" + "─" * 14 + "┬" + "─" * 22 + "┐",
        "│ {:^4} │ {:^30} │ {:^12} │ {:^20} │".format("ID", "Title", "Status", "Created At"),
        "├" + "─" * 6 + "┼" + "─" * 32 + "┼" + "─" * 14 + "┼" + "─" * 22 + "┤",
    ]
    
    # Rows
    for task in tasks:
        title = task.get("title", "")[:28]
        if len(task.get("title", "")) > 28:
            title += ".."
        status = task.get("status", "")
        created = task.get("created_at", "")[:19] if task.get("created_at") else ""
        
        lines.append(
            "│ {:^4} │ {:^30} │ {:^12} │ {:^20} │".format(
                task.get("id", ""),
                title,
                status,
                created
            )
        )
    
    lines.append("└" + "─" * 6 + "┴" + "─" * 32 + "┴" + "─" * 14 + "┴" + "─" * 22 + "┘")
    
    return "\n".join(lines)


def format_result(tool_name: str, result: dict) -> str:
    """Format the result based on tool type."""
    if "error" in result:
        return f"❌ Error: [{result['error'].get('code', 'ERROR')}] {result['error'].get('message', 'Unknown error')}"
    
    if tool_name == "list_tasks":
        tasks = result.get("tasks", [])
        count = len(tasks)
        output = f"📋 Found {count} task(s):\n\n"
        output += format_task_table(tasks)
        return output
    
    elif tool_name == "get_task_by_id":
        task = result.get("task", {})
        output = f"📝 Task Details:\n\n"
        output += json.dumps(task, ensure_ascii=False, indent=2)
        return output
    
    elif tool_name == "create_task":
        task = result.get("task", {})
        output = f"✅ Task created successfully!\n\n"
        output += json.dumps(task, ensure_ascii=False, indent=2)
        return output
    
    elif tool_name == "update_task_status":
        task = result.get("task", {})
        output = f"✅ Task status updated successfully!\n\n"
        output += json.dumps(task, ensure_ascii=False, indent=2)
        return output
    
    elif tool_name == "delete_task":
        output = f"✅ Task {result.get('id')} deleted successfully!"
        return output
    
    else:
        return json.dumps(result, ensure_ascii=False, indent=2)


async def run_client():
    """Run the MCP client."""
    print("=" * 60)
    print("🚀 Todo MCP Client")
    print("=" * 60)
    print("\nConnecting to MCP Server...")
    
    # Get the path to the MCP server module
    server_command = sys.executable
    server_args = ["-m", "app.mcp_server"]
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=server_command,
        args=server_args,
        env={**os.environ}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                print("✅ Connected to MCP Server!")
                print("\n" + "-" * 60)
                print("Available commands (Persian/English):")
                print("  - لیست تسک‌ها رو نشون بده / show all tasks")
                print("  - لیست pending رو نشون بده / list pending tasks")
                print("  - یک تسک جدید با عنوان X بساز / create task with title X")
                print("  - وضعیت تسک 5 رو done کن / update task 5 to done")
                print("  - جزئیات تسک 3 / show task 3 details")
                print("  - تسک 2 رو حذف کن / delete task 2")
                print("  - exit / quit / خروج")
                print("-" * 60 + "\n")
                
                while True:
                    try:
                        user_input = input("You: ").strip()
                        
                        if not user_input:
                            continue
                        
                        if user_input.lower() in ["exit", "quit", "خروج", "q"]:
                            print("\n👋 Goodbye!")
                            break
                        
                        # Parse user input
                        tool_name, arguments = parse_user_input(user_input)
                        
                        if not tool_name:
                            print("\n❓ I didn't understand that. Please try one of the supported commands.")
                            print("   متوجه نشدم. لطفاً یکی از دستورات پشتیبانی شده را امتحان کنید.\n")
                            continue
                        
                        print(f"\n🔧 Calling: {tool_name}")
                        if arguments:
                            print(f"   Arguments: {arguments}")
                        
                        # Call the tool
                        result = await session.call_tool(tool_name, arguments)
                        
                        # Parse and format result
                        if result.content:
                            try:
                                result_text = result.content[0].text
                                result_data = json.loads(result_text)
                                formatted = format_result(tool_name, result_data)
                                print(f"\n{formatted}\n")
                            except (json.JSONDecodeError, IndexError, AttributeError):
                                print(f"\n{result.content}\n")
                        else:
                            print("\n❌ No response from server\n")
                    
                    except KeyboardInterrupt:
                        print("\n\n👋 Goodbye!")
                        break
                    except Exception as e:
                        print(f"\n❌ Error: {e}\n")
    
    except Exception as e:
        print(f"❌ Failed to connect to MCP Server: {e}")
        print("\nMake sure the DATABASE_URL environment variable is set correctly.")
        sys.exit(1)


def main():
    """Main entry point."""
    asyncio.run(run_client())


if __name__ == "__main__":
    main()
