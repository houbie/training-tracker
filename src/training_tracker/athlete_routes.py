"""API routes for athletes."""

from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from training_tracker.models import Athlete, AthleteInput, Statistics
from training_tracker.storage import (
    athlete_exists,
    count_sessions_by_athlete,
    create_athlete,
    delete_athlete,
    delete_sessions_by_athlete,
    get_all_athletes,
    get_athlete,
    get_sessions_by_athlete,
    update_athlete,
)

router = APIRouter(prefix="/v1/athletes", tags=["athletes"])


@router.get("", response_model=list[Athlete])
async def list_athletes():
    """Retrieve a list of all athletes."""
    return list(get_all_athletes().values())


@router.post("", response_model=Athlete, status_code=201)
async def create_athlete_endpoint(athlete_input: AthleteInput):
    """Create a new athlete."""
    athlete_id = str(uuid4())

    athlete = Athlete(
        id=athlete_id,
        name=athlete_input.name,
    )

    create_athlete(athlete)

    return athlete


@router.get("/{id}", response_model=Athlete)
async def get_athlete_endpoint(id: str):
    """Retrieve details of a single athlete by ID."""
    if not (athlete := get_athlete(id)):
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Athlete with id '{id}' not found"},
        )
    return athlete


@router.get("/{id}/statistics", response_model=Statistics)
async def get_athlete_statistics(id: str):
    """Retrieve aggregated statistics for a specific athlete."""
    if not athlete_exists(id):
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Athlete with id '{id}' not found"},
        )

    sessions = get_sessions_by_athlete(id)
    total_sessions = len(sessions)
    total_duration = sum(s.duration for s in sessions)
    total_distance = sum(s.distance for s in sessions)

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


@router.put("/{id}", response_model=Athlete)
async def update_athlete_endpoint(id: str, athlete_input: AthleteInput):
    """Update an existing athlete."""
    if not athlete_exists(id):
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Athlete with id '{id}' not found"},
        )

    updated_athlete = Athlete(
        id=id,
        name=athlete_input.name,
    )

    update_athlete(updated_athlete)

    return updated_athlete


@router.delete("/{id}", status_code=204)
async def delete_athlete_endpoint(
    id: str,
    cascade: bool = Query(False, description="If true, also delete all training sessions for this athlete"),
):
    """Delete an athlete. Optionally cascade delete their training sessions."""
    if not athlete_exists(id):
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Athlete with id '{id}' not found"},
        )

    # Check if athlete has training sessions
    session_count = count_sessions_by_athlete(id)
    if session_count > 0 and not cascade:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ATHLETE_HAS_SESSIONS",
                "message": f"Cannot delete athlete. They have {session_count} training session(s). "
                "Use cascade=true to delete athlete and all their sessions.",
                "sessionCount": session_count,
            },
        )

    # Delete sessions if cascade is enabled
    if cascade:
        delete_sessions_by_athlete(id)

    delete_athlete(id)
    return Response(status_code=204)
