# Todo Service

یک سرویس مدیریت تسک (Todo) با REST API و MCP Server/Client

## 🆕 Quick Start با FastMCP

سریع‌ترین روش برای شروع:

```bash
# 1. نصب dependencies
uv sync

# 2. راه‌اندازی دیتابیس (در یک ترمینال)
docker compose up postgres -d

# 3. اجرای FastMCP Server (در یک ترمینال)
uv run mcp dev app/mcp_server/fastmcp_server.py

# 4. اجرای FastMCP Client (در ترمینال دیگر)
uv run python app/mcp_client/fastmcp_client.py
```

🎉 حالا می‌توانید دستورات فارسی یا انگلیسی را تایپ کنید!

```
You: لیست تسک‌ها رو نشون بده
You: یک تسک جدید با عنوان "خرید نان" بساز
You: help
```

## � مستندات

- 📖 [راهنمای کامل FastMCP](FASTMCP_USAGE.py) - همه چیز درباره FastMCP
- 🚀 [Quick Start](#-quick-start-با-fastmcp) - شروع سریع
- 🔧 [نصب و راه‌اندازی](#-نصب) - راهنمای نصب
- 🤖 [MCP Server](#-mcp-server) - مستندات سرور
- 💬 [MCP Client](#-mcp-client-cli) - مستندات کلاینت
- 📋 [REST API](#-استفاده-از-api) - مستندات API

## �🚀 ویژگی‌ها

- **REST API** با FastAPI برای عملیات CRUD روی تسک‌ها
- **MCP Server** مبتنی بر stdio با استفاده از پکیج رسمی `mcp`
- **FastMCP Server** پیاده‌سازی جدید با FastMCP برای راحتی و سرعت بیشتر
- **MCP Client** با پشتیبانی از دستورات فارسی و انگلیسی
- **FastMCP Client** کلاینت تعاملی با پشتیبانی کامل از prompts
- **PostgreSQL** به عنوان دیتابیس
- **SQLModel** برای ORM
- **Docker Compose** برای اجرای آسان

## 📋 پیش‌نیازها

- Python 3.11+ (ترجیحاً 3.12)
- [uv](https://docs.astral.sh/uv/) - مدیریت پروژه Python
- Docker و Docker Compose (اختیاری)
- PostgreSQL (اگر از Docker استفاده نمی‌کنید)

## 🛠️ نصب

### 1. نصب uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. کلون پروژه

```bash
git clone https://github.com/msinamsina/To-Do-Service.git
cd To-Do-Service
```

### 3. ایجاد محیط مجازی و نصب وابستگی‌ها

```bash
uv venv
uv sync
```

### 4. تنظیم متغیرهای محیطی

```bash
cp .env.example .env
# ویرایش فایل .env در صورت نیاز
```

## 🐳 اجرا با Docker Compose

### راه‌اندازی دیتابیس و API

```bash
docker compose up -d
```

این دستور PostgreSQL و API را راه‌اندازی می‌کند:
- PostgreSQL: `localhost:5432`
- API: `http://localhost:8000`

### مشاهده لاگ‌ها

```bash
docker compose logs -f
```

### توقف سرویس‌ها

```bash
docker compose down
```

## 💻 اجرای محلی (بدون Docker)

### 1. راه‌اندازی PostgreSQL

می‌توانید PostgreSQL را به صورت محلی نصب کنید یا فقط دیتابیس را با Docker اجرا کنید:

```bash
docker compose up postgres -d
```

### 2. اجرای REST API

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API در آدرس `http://localhost:8000` در دسترس خواهد بود.

### 3. اجرای MCP Server (stdio)

#### نسخه استاندارد (mcp)
```bash
uv run python -m app.mcp_server
```

#### نسخه FastMCP (توصیه می‌شود)
```bash
uv run mcp dev app/mcp_server/fastmcp_server
```

**توجه:** MCP Server مبتنی بر stdio است و برای ارتباط با کلاینت‌های MCP طراحی شده است.

![MCP Inspector](assets/tools.JPG)

![MCP Inspector](assets/prompts.JPG)


### 4. اجرای MCP Client

#### کلاینت استاندارد
```bash
uv run python -m app.mcp_client
```

#### کلاینت FastMCP (با پشتیبانی prompt)
```bash
uv run python app/mcp_client/fastmcp_client.py
```

## 📚 استفاده از API

### مستندات API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### نمونه درخواست‌ها با curl

#### لیست تمام تسک‌ها
```bash
curl -X GET "http://localhost:8000/api/v1/tasks"
```

#### لیست تسک‌ها با فیلتر وضعیت
```bash
curl -X GET "http://localhost:8000/api/v1/tasks?status=pending"
```

#### دریافت یک تسک
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1"
```

#### ایجاد تسک جدید
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "خرید نان",
    "description": "از نانوایی سر کوچه",
    "status": "pending"
  }'
```

#### بروزرسانی تسک
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "خرید نان و شیر",
    "status": "in_progress"
  }'
```

#### حذف تسک
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

## 🤖 MCP Server

### پکیج‌ها و نسخه‌ها

این پروژه شامل دو پیاده‌سازی MCP Server است:

1. **MCP Standard** (`app/mcp_server/server.py`): استفاده از پکیج رسمی `mcp` (نسخه >= 1.0.0)
2. **FastMCP** (`app/mcp_server/fastmcp_server.py`): استفاده از `fastmcp` (نسخه >= 0.2.0) - **توصیه می‌شود**

### مزایای FastMCP

- ✅ **سینتکس ساده‌تر**: استفاده از دکوراتورها برای تعریف tools و prompts
- ✅ **Type Safety**: پشتیبانی کامل از type hints و Pydantic
- ✅ **Prompts**: امکان تعریف prompts برای راهنمایی کاربران
- ✅ **Development Mode**: اجرای آسان با `mcp dev`
- ✅ **خطایابی بهتر**: پیام‌های خطای واضح‌تر

### اجرای FastMCP Server در حالت توسعه

```bash
uv run mcp dev app/mcp_server/fastmcp_server.py
```

این دستور سرور را در حالت development اجرا می‌کند و تغییرات را به صورت خودکار reload می‌کند.

### ابزارهای موجود (Tools)

| Tool Name | Description | Input |
|-----------|-------------|-------|
| `list_tasks` | لیست تمام تسک‌ها | `{"status": "pending\|in_progress\|done"}` (اختیاری) |
| `get_task_by_id` | دریافت جزئیات تسک | `{"task_id": <int>}` |
| `create_task` | ایجاد تسک جدید | `{"title": <str>, "description": <str?>, "status": <str?>}` |
| `update_task` | بروزرسانی تسک (FastMCP) | `{"task_id": <int>, "title": <str?>, "description": <str?>, "status": <str?>}` |
| `update_task_status` | بروزرسانی وضعیت | `{"task_id": <int>, "status": <str>}` |
| `delete_task` | حذف تسک | `{"task_id": <int>}` |

### Prompts موجود (فقط FastMCP)

FastMCP Server شامل prompts مفید برای راهنمایی کاربران است:

| Prompt Name | Description |
|-------------|-------------|
| `task_management_guide` | راهنمای جامع مدیریت تسک‌ها |
| `task_status_workflow` | توضیح چرخه عمر وضعیت‌های تسک |
| `create_task_template` | الگوی ایجاد تسک با ساختار مناسب |
| `daily_task_summary` | الگوی خلاصه روزانه تسک‌ها |

### اجرای MCP Server

#### نسخه استاندارد
```bash
uv run python -m app.mcp_server
```

#### نسخه FastMCP (پیشنهادی)
```bash
uv run mcp dev app/mcp_server/fastmcp_server.py
```

## 💬 MCP Client (CLI)

### دو نوع کلاینت

#### 1. کلاینت استاندارد (`app/mcp_client/cli.py`)
کلاینت CLI با پشتیبانی از دستورات فارسی و انگلیسی.

#### 2. کلاینت FastMCP (`app/mcp_client/fastmcp_client.py`) - **پیشنهادی**
کلاینت پیشرفته با پشتیبانی از:
- تمام دستورات فارسی و انگلیسی
- دسترسی به Prompts
- نمایش بهتر نتایج
- خطایابی بهتر

### اجرا

#### کلاینت استاندارد
```bash
uv run python -m app.mcp_client
```

#### کلاینت FastMCP (پیشنهادی)
```bash
uv run python app/mcp_client/fastmcp_client.py
```

### نمونه دستورات

#### لیست تسک‌ها
```
You: لیست تسک‌ها رو نشون بده
You: show all tasks
You: لیست pending رو نشون بده
You: list done tasks
```

#### ایجاد تسک
```
You: یک تسک جدید با عنوان خرید نان بساز
You: create task with title "Buy groceries"
You: تسک جدید با عنوان "جلسه تیم" بساز
```

#### بروزرسانی وضعیت
```
You: وضعیت تسک 5 رو done کن
You: update task 3 to in_progress
You: تسک 2 رو انجام‌شده کن
```

#### جزئیات تسک
```
You: جزئیات تسک 3
You: show task 1 details
```

#### حذف تسک
```
You: تسک 2 رو حذف کن
You: delete task 5
```

#### دسترسی به Prompts (فقط FastMCP Client)
```
You: help
You: راهنما
You: workflow
You: جریان کار
You: daily
You: روزانه
```

### نمونه خروجی

```
============================================================
🚀 Todo FastMCP Client
============================================================

Connecting to FastMCP Server...
✅ Connected to FastMCP Server!

📦 Available tools: 7
📝 Available prompts: 4

------------------------------------------------------------
Available commands (Persian/English):
  - لیست تسک‌ها رو نشون بده / show all tasks
  - لیست pending رو نشون بده / list pending tasks
  - یک تسک جدید با عنوان X بساز / create task with title X
  - وضعیت تسک 5 رو done کن / update task 5 to done
  - جزئیات تسک 3 / show task 3 details
  - تسک 2 رو حذف کن / delete task 2
  - help / راهنما - Show task management guide
  - workflow / جریان کار - Show status workflow
  - daily / روزانه - Show daily summary template
  - exit / quit / خروج
------------------------------------------------------------

You: لیست تسک‌ها رو نشون بده

🔧 Calling: list_tasks

📋 Found 2 task(s):

┌──────┬────────────────────────────────┬──────────────┬──────────────────────┐
│  ID  │             Title              │    Status    │      Created At      │
├──────┼────────────────────────────────┼──────────────┼──────────────────────┤
│  1   │          خرید نان              │   pending    │   2026-01-05T10:00   │
│  2   │          جلسه تیم              │  in_progress │   2026-01-05T11:00   │
└──────┴────────────────────────────────┴──────────────┴──────────────────────┘

You: یک تسک جدید با عنوان تمرین ورزشی بساز

🔧 Calling: create_task
   Arguments: {'title': 'تمرین ورزشی', 'status': 'pending'}

✅ Task details:

{
  "id": 3,
  "title": "تمرین ورزشی",
  "description": null,
  "status": "pending",
  "created_at": "2026-01-05T12:00:00",
  "updated_at": "2026-01-05T12:00:00"
}

You: help

📖 Getting prompt: task_management_guide

============================================================
# Task Management Guide

## Available Operations

### 1. List Tasks
- View all tasks or filter by status (pending, in_progress, done)
- Example: "Show me all pending tasks"

### 2. Get Task Details
- Retrieve detailed information about a specific task by ID
- Example: "Show details for task 5"

[... بقیه راهنما ...]
============================================================

You: exit

👋 Goodbye!
```

## 📁 ساختار پروژه

```
To-Do-Service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py       # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # SQLModel Task model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py          # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic layer
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py     # Task API routes
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── server.py        # MCP Server (standard)
│   │   └── fastmcp_server.py # FastMCP Server (recommended)
│   └── mcp_client/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py           # MCP Client CLI (standard)
│       └── fastmcp_client.py # FastMCP Client (recommended)
├── pyproject.toml           # Project configuration
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── .env.example             # Environment variables template
├── .env                     # Environment variables (not in git)
└── README.md                # This file
```

## 📊 جدول tasks

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | شناسه یکتا |
| title | VARCHAR(200) | NOT NULL | عنوان تسک |
| description | TEXT | NULLABLE | توضیحات |
| status | VARCHAR(50) | DEFAULT 'pending' | وضعیت: pending, in_progress, done |
| created_at | TIMESTAMP | DEFAULT NOW() | زمان ایجاد |
| updated_at | TIMESTAMP | DEFAULT NOW() | زمان آخرین بروزرسانی |

## 🔧 متغیرهای محیطی

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | آدرس اتصال به PostgreSQL | postgresql://postgres:postgres@localhost:5432/todo_db |
| API_HOST | هاست API | 0.0.0.0 |
| API_PORT | پورت API | 8000 |
| MCP_SERVER_NAME | نام MCP Server | todo-mcp-server |

## ✅ چک‌لیست نیازمندی‌ها

- [x] Python 3.11+ با FastAPI
- [x] SQLModel برای ORM
- [x] PostgreSQL با اتصال از طریق DATABASE_URL
- [x] مدیریت پروژه با uv
- [x] جدول tasks با تمام ستون‌های مورد نیاز
- [x] Status به صورت Enum
- [x] updated_at در هر update بروزرسانی می‌شود
- [x] REST API کامل (GET, POST, PUT, PATCH, DELETE)
- [x] فیلتر بر اساس status
- [x] Schemaهای جدا برای Create/Update/Read
- [x] مدیریت خطا (400, 404, 500)
- [x] MCP Server با پکیج رسمی `mcp` روی stdio
- [x] پنج Tool: list_tasks, get_task_by_id, create_task, update_task_status, delete_task
- [x] MCP Client با پشتیبانی فارسی و انگلیسی
- [x] Rule-based parsing برای دستورات
- [x] Docker Compose برای PostgreSQL و API
- [x] README کامل با مثال‌ها
- [x] ساختار پروژه لایه‌ای و منظم
- [x] Type hints و validation

## 📝 فرضیات و پیشنهادات

### فرضیات
1. **Sync vs Async**: از SQLModel به صورت synchronous استفاده شده چون SQLModel هنوز پشتیبانی کامل async ندارد.
2. **MCP Protocol**: از نسخه stdio پروتکل MCP استفاده شده که مناسب اجرای محلی است.
3. **Parsing**: از rule-based parsing برای کلاینت استفاده شده که می‌تواند با LLM جایگزین شود.

### پیشنهادات برای بهبود
1. اضافه کردن migration با Alembic
2. اضافه کردن تست‌های واحد و یکپارچگی
3. پیاده‌سازی authentication و authorization
4. اضافه کردن logging ساختاریافته
5. استفاده از Redis برای caching
6. اضافه کردن rate limiting

## 🆕 FastMCP: پیاده‌سازی جدید

### چرا FastMCP؟

FastMCP یک wrapper ساده و قدرتمند برای MCP است که توسعه سرورها را بسیار ساده‌تر می‌کند:

#### مزایا
- **سینتکس ساده**: استفاده از دکوراتورها به جای کدهای boilerplate
- **Type Safety کامل**: پشتیبانی از Pydantic و type hints
- **Prompts**: امکان تعریف prompts برای راهنمایی کاربران
- **Development Mode**: reload خودکار در حین توسعه
- **خطایابی بهتر**: پیام‌های خطای واضح‌تر و مفیدتر

#### مقایسه کد

**MCP Standard** (server.py):
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_tasks",
            description="...",
            inputSchema={
                "type": "object",
                "properties": {...},
                "required": []
            }
        ),
        # بقیه tools...
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_tasks":
        return await handle_list_tasks(arguments)
    # بقیه handlers...
```

**FastMCP** (fastmcp_server.py):
```python
@mcp.tool()
def list_tasks(
    status: Optional[str] = Field(None, description="Filter by status")
) -> dict:
    """List all tasks. Optionally filter by status."""
    service = get_service()
    status_enum = validate_status(status) if status else None
    tasks = service.get_all_tasks(status=status_enum)
    return {"tasks": [format_task(task) for task in tasks]}
```

همانطور که می‌بینید، FastMCP کد را بسیار ساده‌تر و خواناتر می‌کند!

### Tools موجود در FastMCP

تمام 7 tool در FastMCP پیاده‌سازی شده‌اند:
1. `list_tasks` - لیست تسک‌ها با فیلتر اختیاری
2. `get_task_by_id` - دریافت جزئیات یک تسک
3. `create_task` - ایجاد تسک جدید
4. `update_task` - بروزرسانی کامل تسک (title, description, status)
5. `update_task_status` - بروزرسانی سریع وضعیت
6. `delete_task` - حذف تسک

### Prompts موجود در FastMCP

FastMCP امکان تعریف prompts را می‌دهد که برای راهنمایی کاربران بسیار مفید است:

1. **task_management_guide**: راهنمای جامع مدیریت تسک‌ها
2. **task_status_workflow**: توضیح چرخه عمر وضعیت‌های تسک با نمودار
3. **create_task_template**: الگوی ایجاد تسک با ساختار مناسب
4. **daily_task_summary**: الگوی خلاصه روزانه برای review و planning

### نحوه استفاده

#### اجرای سرور در حالت توسعه:
```bash
uv run mcp dev app/mcp_server/fastmcp_server
```

#### اجرای کلاینت:
```bash
uv run python app/mcp_client/fastmcp_client.py
```

#### دسترسی به Prompts:
```
You: help          # نمایش راهنمای کامل
You: workflow      # نمایش workflow وضعیت‌ها
You: daily         # نمایش الگوی خلاصه روزانه
```

### نکات مهم

1. **Dependencies**: FastMCP نیاز به نصب `fastmcp>=0.2.0` دارد که در pyproject.toml اضافه شده است.
2. **Database Init**: سرور FastMCP به صورت خودکار دیتابیس را initialize می‌کند.
3. **Error Handling**: خطاها به صورت ساده‌تر و واضح‌تر برگردانده می‌شوند.
4. **Development**: در حالت dev، تغییرات به صورت خودکار reload می‌شوند.

## 📊 خلاصه فایل‌های جدید

### فایل‌های اضافه شده:

1. **[app/mcp_server/fastmcp_server.py](app/mcp_server/fastmcp_server.py)**
   - پیاده‌سازی MCP Server با FastMCP
   - 6 Tool: list_tasks, get_task_by_id, create_task, update_task, update_task_status, delete_task
   - 4 Prompt: task_management_guide, task_status_workflow, create_task_template, daily_task_summary
   - قابل اجرا با: `uv run mcp dev app/mcp_server/fastmcp_server`

2. **[app/mcp_client/fastmcp_client.py](app/mcp_client/fastmcp_client.py)**
   - کلاینت تعاملی FastMCP
   - پشتیبانی کامل از دستورات فارسی و انگلیسی
   - نمایش جدولی نتایج
   - دسترسی به Prompts
   - قابل اجرا با: `uv run python app/mcp_client/fastmcp_client.py`

3. **[FASTMCP_USAGE.py](FASTMCP_USAGE.py)**
   - راهنمای کامل استفاده از FastMCP
   - مستندات تمام Tools و Prompts
   - نمونه دستورات و نکات مهم

### دستورات اصلی:

```bash
# سرور FastMCP (حالت توسعه)
uv run mcp dev app/mcp_server/fastmcp_server

# کلاینت FastMCP
uv run python app/mcp_client/fastmcp_client.py

# سرور استاندارد MCP
uv run python -m app.mcp_server

# کلاینت استاندارد MCP
uv run python -m app.mcp_client
```

## 🎯 توصیه‌های استفاده

### برای توسعه:
✅ استفاده از **FastMCP Server** (hot reload، خطایابی بهتر، prompts)
✅ استفاده ا�� **FastMCP Client** (UI بهتر، دسترسی به prompts)

### برای آشنایی با MCP Protocol:
✅ بررسی **MCP Standard Server** (app/mcp_server/server.py)
✅ مقایسه دو پیاده‌سازی برای یادگیری

## 📄 License

MIT License