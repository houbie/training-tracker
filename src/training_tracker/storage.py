"""In-memory storage for training sessions."""

import datetime
from typing import Dict

from training_tracker.models import Athlete, TrainingSession

# In-memory storage (replace with database in production)
athletes_db: Dict[str, Athlete] = {}
training_sessions_db: Dict[str, TrainingSession] = {}


def get_all_sessions() -> Dict[str, TrainingSession]:
    """Get all training sessions."""
    return training_sessions_db


def get_session(session_id: str) -> TrainingSession | None:
    """Get a training session by ID."""
    return training_sessions_db.get(session_id)


def create_session(session: TrainingSession) -> None:
    """Create a new training session."""
    training_sessions_db[session.id] = session


def update_session(session: TrainingSession) -> None:
    """Update an existing training session."""
    training_sessions_db[session.id] = session


def delete_session(session_id: str) -> None:
    """Delete a training session."""
    if session_id in training_sessions_db:
        del training_sessions_db[session_id]


def session_exists(session_id: str) -> bool:
    """Check if a training session exists."""
    return session_id in training_sessions_db


# Athlete operations
def get_all_athletes() -> Dict[str, Athlete]:
    """Get all athletes."""
    return athletes_db


def get_athlete(athlete_id: str) -> Athlete | None:
    """Get an athlete by ID."""
    return athletes_db.get(athlete_id)


def create_athlete(athlete: Athlete) -> None:
    """Create a new athlete."""
    athletes_db[athlete.id] = athlete


def update_athlete(athlete: Athlete) -> None:
    """Update an existing athlete."""
    athletes_db[athlete.id] = athlete


def delete_athlete(athlete_id: str) -> None:
    """Delete an athlete."""
    if athlete_id in athletes_db:
        del athletes_db[athlete_id]


def athlete_exists(athlete_id: str) -> bool:
    """Check if an athlete exists."""
    return athlete_id in athletes_db


def get_sessions_by_athlete(athlete_id: str) -> list[TrainingSession]:
    """Get all training sessions for a specific athlete."""
    return [session for session in training_sessions_db.values() if session.athlete_id == athlete_id]


def count_sessions_by_athlete(athlete_id: str) -> int:
    """Count training sessions for a specific athlete."""
    return len(get_sessions_by_athlete(athlete_id))


def delete_sessions_by_athlete(athlete_id: str) -> int:
    """Delete all training sessions for a specific athlete. Returns count of deleted sessions."""
    sessions_to_delete = [session.id for session in training_sessions_db.values() if session.athlete_id == athlete_id]
    for session_id in sessions_to_delete:
        del training_sessions_db[session_id]
    return len(sessions_to_delete)


def initialize_example_data() -> None:
    """Initialize storage with example athletes and training sessions."""
    # Create example athletes
    example_athletes = [
        Athlete(id="athlete-1", name="John Doe"),
        Athlete(id="athlete-2", name="Jane Smith"),
    ]

    for athlete in example_athletes:
        athletes_db[athlete.id] = athlete

    # Create example training sessions
    example_sessions = [
        TrainingSession(
            id="a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
            athlete_id="athlete-1",
            athlete_name="John Doe",
            date=datetime.date(2025, 10, 20),
            duration=45.0,
            distance=8.5,
            notes="Morning run with intervals",
            createdAt=datetime.datetime(2025, 10, 20, 8, 0, 0),
            updatedAt=datetime.datetime(2025, 10, 20, 8, 0, 0),
        ),
        TrainingSession(
            id="b2c3d4e5-f6a7-4b6c-9d0e-1f2a3b4c5d6e",
            athlete_id="athlete-1",
            athlete_name="John Doe",
            date=datetime.date(2025, 10, 21),
            duration=60.0,
            distance=12.0,
            notes="Long steady run",
            createdAt=datetime.datetime(2025, 10, 21, 7, 30, 0),
            updatedAt=datetime.datetime(2025, 10, 21, 7, 30, 0),
        ),
        TrainingSession(
            id="c3d4e5f6-a7b8-4c7d-0e1f-2a3b4c5d6e7f",
            athlete_id="athlete-2",
            athlete_name="Jane Smith",
            date=datetime.date(2025, 10, 22),
            duration=30.0,
            distance=5.0,
            notes="Easy recovery run",
            createdAt=datetime.datetime(2025, 10, 22, 18, 0, 0),
            updatedAt=datetime.datetime(2025, 10, 22, 18, 0, 0),
        ),
        TrainingSession(
            id="d4e5f6a7-b8c9-4d8e-1f2a-3b4c5d6e7f8a",
            athlete_id="athlete-2",
            athlete_name="Jane Smith",
            date=datetime.date(2025, 10, 23),
            duration=50.0,
            distance=10.0,
            notes="Tempo run feeling strong",
            createdAt=datetime.datetime(2025, 10, 23, 6, 45, 0),
            updatedAt=datetime.datetime(2025, 10, 23, 6, 45, 0),
        ),
    ]

    for session in example_sessions:
        training_sessions_db[session.id] = session
