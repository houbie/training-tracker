"""API routes for the Training Tracker."""

import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from training_tracker.database import (
    create_session,
    delete_session,
    get_all_sessions,
    get_athlete,
    get_session,
    session_exists,
    update_session,
)
from training_tracker.models import (
    Pagination,
    Statistics,
    TrainingSession,
    TrainingSessionInput,
    TrainingSessionListResponse,
)

router = APIRouter(prefix="/v1", tags=["training-sessions"])


@router.get("/training-sessions", response_model=TrainingSessionListResponse)
async def list_training_sessions(
    startDate: Optional[datetime.date] = Query(None, description="Filter sessions on or after this date (YYYY-MM-DD)"),
    endDate: Optional[datetime.date] = Query(None, description="Filter sessions on or before this date (YYYY-MM-DD)"),
    athleteId: Optional[str] = Query(None, description="Filter sessions by athlete ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip for pagination"),
):
    """Retrieve a list of all training sessions with optional filtering."""
    filtered_sessions = sorted(
        [
            session
            for session in get_all_sessions().values()
            if (not startDate or session.date >= startDate)
            and (not endDate or session.date <= endDate)
            and (not athleteId or session.athlete_id == athleteId)
        ],
        key=lambda x: x.date,
        reverse=True,
    )

    total = len(filtered_sessions)
    paginated_sessions = filtered_sessions[offset : offset + limit]
    has_more = offset + limit < total

    return TrainingSessionListResponse(
        data=paginated_sessions,
        pagination=Pagination(total=total, limit=limit, offset=offset, hasMore=has_more),
    )


@router.post("/training-sessions", response_model=TrainingSession, status_code=201)
async def create_training_session(session_input: TrainingSessionInput):
    """Add a new training session to the tracker."""
    # Verify athlete exists
    athlete = get_athlete(session_input.athlete_id)
    if not athlete:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Athlete with id '{session_input.athlete_id}' not found"},
        )

    session_id = str(uuid4())
    now = datetime.datetime.now(datetime.timezone.utc)

    session = TrainingSession(
        id=session_id,
        athlete_id=session_input.athlete_id,
        athlete_name=athlete.name,
        date=session_input.date,
        duration=session_input.duration,
        distance=session_input.distance,
        notes=session_input.notes,
        createdAt=now,
        updatedAt=now,
    )

    create_session(session)

    return session


@router.get("/training-sessions/statistics", response_model=Statistics)
async def get_training_statistics(
    startDate: Optional[datetime.date] = Query(None, description="Start date for statistics (YYYY-MM-DD)"),
    endDate: Optional[datetime.date] = Query(None, description="End date for statistics (YYYY-MM-DD)"),
):
    """Retrieve aggregated statistics for training sessions."""
    filtered_sessions = [
        session
        for session in get_all_sessions().values()
        if (not startDate or session.date >= startDate) and (not endDate or session.date <= endDate)
    ]

    total_sessions = len(filtered_sessions)
    total_duration = sum(s.duration for s in filtered_sessions)
    total_distance = sum(s.distance for s in filtered_sessions)

    avg_duration = total_duration / total_sessions if total_sessions > 0 else 0.0
    avg_distance = total_distance / total_sessions if total_sessions > 0 else 0.0
    avg_pace = total_duration / total_distance if total_distance > 0 else 0.0

    return Statistics(
        totalSessions=total_sessions,
        totalDuration=round(total_duration, 2),
        totalDistance=round(total_distance, 2),
        averageDuration=round(avg_duration, 2),
        averageDistance=round(avg_distance, 2),
        averagePace=round(avg_pace, 2),
    )


@router.get("/training-sessions/{id}", response_model=TrainingSession)
async def get_training_session(id: str):
    """Retrieve details of a single training session by ID."""
    session = get_session(id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Training session with id '{id}' not found"},
        )

    return session


@router.put("/training-sessions/{id}", response_model=TrainingSession)
async def update_training_session(id: str, session_input: TrainingSessionInput):
    """Update an existing training session."""
    existing_session = get_session(id)
    if not existing_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Training session with id '{id}' not found"},
        )

    # Verify athlete exists
    athlete = get_athlete(session_input.athlete_id)
    if not athlete:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Athlete with id '{session_input.athlete_id}' not found"},
        )

    now = datetime.datetime.now(datetime.timezone.utc)

    updated_session = TrainingSession(
        id=id,
        athlete_id=session_input.athlete_id,
        athlete_name=athlete.name,
        date=session_input.date,
        duration=session_input.duration,
        distance=session_input.distance,
        notes=session_input.notes,
        createdAt=existing_session.createdAt,
        updatedAt=now,
    )

    update_session(updated_session)

    return updated_session


@router.delete("/training-sessions/{id}", status_code=204)
async def delete_training_session(id: str):
    """Remove a training session from the tracker."""
    if not session_exists(id):
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Training session with id '{id}' not found"},
        )

    delete_session(id)
    return Response(status_code=204)
