"""Pydantic models for the Training Tracker API."""

import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Athlete(BaseModel):
    """Athlete model."""

    id: str = Field(description="Unique identifier for the athlete")
    name: str = Field(description="Name of the athlete")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "athlete-123",
                "name": "John Doe",
            }
        }
    )


class AthleteInput(BaseModel):
    """Input model for creating or updating an athlete."""

    name: str = Field(description="Name of the athlete")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
            }
        }
    )


class TrainingSessionInput(BaseModel):
    """Input model for creating or updating a training session."""

    athlete_id: str = Field(description="ID of the athlete")
    date: datetime.date = Field(description="Date of the training session (YYYY-MM-DD)")
    duration: float = Field(ge=0, description="Duration of the session in minutes")
    distance: float = Field(ge=0, description="Distance covered in kilometers")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes or comments about the session")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "athlete_id": "athlete-123",
                "date": "2025-10-23",
                "duration": 45.5,
                "distance": 8.5,
                "notes": "Morning run with intervals",
            }
        }
    )


class TrainingSession(BaseModel):
    """Complete training session model with metadata."""

    id: str = Field(description="Unique identifier for the training session")
    athlete_id: str = Field(description="ID of the athlete")
    athlete_name: str = Field(description="Name of the athlete")
    date: datetime.date = Field(description="Date of the training session (YYYY-MM-DD)")
    duration: float = Field(ge=0, description="Duration of the session in minutes")
    distance: float = Field(ge=0, description="Distance covered in kilometers")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes or comments about the session")
    createdAt: datetime.datetime = Field(description="Timestamp when the session was created")
    updatedAt: datetime.datetime = Field(description="Timestamp when the session was last updated")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "athlete_id": "athlete-123",
                "athlete_name": "John Doe",
                "date": "2025-10-23",
                "duration": 45.5,
                "distance": 8.5,
                "notes": "Great session with intervals",
                "createdAt": "2025-10-23T10:30:00Z",
                "updatedAt": "2025-10-23T10:30:00Z",
            }
        }
    )


class Pagination(BaseModel):
    """Pagination metadata for list responses."""

    total: int = Field(description="Total number of items")
    limit: int = Field(description="Maximum number of items per page")
    offset: int = Field(description="Number of items skipped")
    hasMore: bool = Field(description="Whether there are more items available")


class TrainingSessionListResponse(BaseModel):
    """Response model for listing training sessions."""

    data: List[TrainingSession]
    pagination: Pagination


class Statistics(BaseModel):
    """Aggregated statistics for training sessions."""

    totalSessions: int = Field(description="Total number of training sessions")
    totalDuration: float = Field(description="Total duration in minutes")
    totalDistance: float = Field(description="Total distance in kilometers")
    averageDuration: float = Field(description="Average duration per session in minutes")
    averageDistance: float = Field(description="Average distance per session in kilometers")
    averagePace: float = Field(description="Average pace in minutes per kilometer")


class Error(BaseModel):
    """Error response model."""

    error: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict] = Field(None, description="Additional error details")
