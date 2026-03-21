"""FastAPI application entrypoint for Agentic SDR system."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.routers import health, webhook, enrichment, sequence
from app.api.routers.assets import router as assets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events.
    """
    # Startup
    # Create storage directory if it doesn't exist
    storage_dir = Path(settings.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Agentic SDR system API with async SQLAlchemy and PostgreSQL",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(enrichment.router)
app.include_router(sequence.router)
app.include_router(assets_router)

# Mount static files for PDF storage
app.mount("/storage/pdfs", StaticFiles(directory=settings.storage_dir), name="pdf_storage")


@app.get("/")
async def root() -> dict:
    """
    Root endpoint with API information.
    
    Returns:
        dict: API information.
    """
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
    }
