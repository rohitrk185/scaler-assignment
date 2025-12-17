"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

# Create database tables (will be replaced by Alembic migrations later)
# Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A backend service replicating core functionalities of Asana",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.get_cors_methods(),
    allow_headers=settings.get_cors_headers(),
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Asana Backend Replica API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# API routes
from app.api.v1 import (
    workspaces, users, projects, tasks, teams, sections,
    attachments, stories, tags, webhooks, custom_fields
)

app.include_router(workspaces.router, prefix=settings.API_V1_PREFIX, tags=["Workspaces"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(projects.router, prefix=settings.API_V1_PREFIX, tags=["Projects"])
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX, tags=["Tasks"])
app.include_router(teams.router, prefix=settings.API_V1_PREFIX, tags=["Teams"])
app.include_router(sections.router, prefix=settings.API_V1_PREFIX, tags=["Sections"])
app.include_router(attachments.router, prefix=settings.API_V1_PREFIX, tags=["Attachments"])
app.include_router(stories.router, prefix=settings.API_V1_PREFIX, tags=["Stories"])
app.include_router(tags.router, prefix=settings.API_V1_PREFIX, tags=["Tags"])
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX, tags=["Webhooks"])
app.include_router(custom_fields.router, prefix=settings.API_V1_PREFIX, tags=["Custom Fields"])

