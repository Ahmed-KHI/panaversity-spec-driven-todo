"""
FastAPI main application.
[Task]: T-011 (Main App)
[From]: spec.md §5, plan.md §3
[Updated]: T-008 (Phase III - Add chat router)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database import create_db_and_tables
from src.routers import auth, tasks, chat

# Create FastAPI app
app = FastAPI(
    title="Todo Management API",
    description="Full-stack task management with user authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(chat.router)  # Phase III: AI chat endpoint


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    create_db_and_tables()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
