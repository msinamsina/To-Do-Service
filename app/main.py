"""FastAPI main application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.routes.tasks import router as tasks_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize database tables
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    yield
    # Shutdown: cleanup if needed
    print("Shutting down...")


app = FastAPI(
    title="Todo Service API",
    description="A RESTful API for managing tasks/todos",
    version="1.0.0",
    lifespan=lifespan,
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with clean messages."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors without exposing internal details."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(tasks_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "Todo Service API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
