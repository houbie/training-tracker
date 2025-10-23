"""Main FastAPI application for Training Tracker."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from training_tracker.athlete_routes import router as athlete_router
from training_tracker.storage import initialize_example_data
from training_tracker.training_session_routes import router as training_session_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    initialize_example_data()
    yield
    # Shutdown (cleanup if needed)


# Initialize FastAPI app
app = FastAPI(
    title="Training Sessions API",
    description="API for tracking training sessions",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(athlete_router)
app.include_router(training_session_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Training Sessions API",
        "version": "1.0.0",
        "description": "API for tracking training sessions",
        "docs": "/docs",
    }


def main():
    """Entry point for running the application."""
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
