# Todo Service

یک سرویس مدیریت تسک (Todo) با REST API و MCP Server/Client

## 🚀 ویژگی‌ها

- **REST API** با FastAPI برای عملیات CRUD روی تسک‌ها
- **MCP Server** مبتنی بر stdio با استفاده از پکیج رسمی `mcp`
- **MCP Client** با پشتیبانی از دستورات فارسی و انگلیسی
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

```bash
uv run python -m app.mcp_server
```

**توجه:** MCP Server مبتنی بر stdio است و برای ارتباط با کلاینت‌های MCP طراحی شده است.

### 4. اجرای MCP Client

```bash
uv run python -m app.mcp_client
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

### پکیج و نسخه

این پروژه از پکیج رسمی `mcp` (نسخه >= 1.0.0) برای پیاده‌سازی MCP Server و Client استفاده می‌کند.

### ابزارهای موجود (Tools)

| Tool Name | Description | Input |
|-----------|-------------|-------|
| `list_tasks` | لیست تمام تسک‌ها | `{"status": "pending\|in_progress\|done"}` (اختیاری) |
| `get_task_by_id` | دریافت جزئیات تسک | `{"id": <int>}` |
| `create_task` | ایجاد تسک جدید | `{"title": <str>, "description": <str?>, "status": <str?>}` |
| `update_task_status` | بروزرسانی وضعیت | `{"id": <int>, "status": <str>}` |
| `delete_task` | حذف تسک | `{"id": <int>}` |

### اجرای MCP Server

```bash
uv run python -m app.mcp_server
```

## 💬 MCP Client (CLI)

کلاینت CLI با پشتیبانی از دستورات فارسی و انگلیسی.

### اجرا

```bash
uv run python -m app.mcp_client
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

### نمونه خروجی

```
============================================================
🚀 Todo MCP Client
============================================================

Connecting to MCP Server...
✅ Connected to MCP Server!

------------------------------------------------------------
Available commands (Persian/English):
  - لیست تسک‌ها رو نشون بده / show all tasks
  - لیست pending رو نشون بده / list pending tasks
  - یک تسک جدید با عنوان X بساز / create task with title X
  - وضعیت تسک 5 رو done کن / update task 5 to done
  - جزئیات تسک 3 / show task 3 details
  - تسک 2 رو حذف کن / delete task 2
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
   Arguments: {'title': 'تمرین ورزشی'}

✅ Task created successfully!

{
  "id": 3,
  "title": "تمرین ورزشی",
  "description": null,
  "status": "pending",
  "created_at": "2026-01-05T12:00:00",
  "updated_at": "2026-01-05T12:00:00"
}

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
│   │   └── server.py        # MCP Server implementation
│   └── mcp_client/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py           # MCP Client CLI
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

## 📄 License

MIT License