"""
FastAPI main application.
[Task]: T-011 (Main App), T-B-005 (Add tags router), T-B-012 (OpenAPI docs update)
[From]: specs/phase1-console-app.specify.md §5, plan.md §3,
        specs/005-phase-v-cloud/phase5-cloud.specify.md §5.1-5.2
[Updated]: T-008 (Phase III - Add chat router), T-B-005 (Phase V - Add tags router)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database import create_db_and_tables
from src.routers import auth, tasks, chat, tags, stats, jobs

# Create FastAPI app
app = FastAPI(
    title="Todo Management API - Phase V",
    description="Full-stack task management with user authentication, advanced features (priorities, due dates, recurring tasks, tags), and AI chatbot assistance",
    version="5.0.0",
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
app.include_router(tags.router)  # Phase V: Tag management
app.include_router(stats.router)  # Phase V: Task statistics
app.include_router(jobs.router)  # Phase V: Job triggers for reminders
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
