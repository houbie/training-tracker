"""DynamoDB storage for training sessions using single table design."""

import datetime
import os
from typing import Dict

import boto3
from boto3.dynamodb.conditions import Attr, Key

from training_tracker.models import Athlete, TrainingSession

# DynamoDB setup - using lazy initialization for testability
_dynamodb_resource = None


def _get_dynamodb():
    """Get or create DynamoDB resource (lazy initialization)."""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        _dynamodb_resource = boto3.resource(
            "dynamodb",
            endpoint_url=os.environ.get("DYNAMODB_ENDPOINT"),  # For local development
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
    return _dynamodb_resource


# Single Table Design:
# Athletes: PK="ATHLETE#<athlete_id>", SK="ATHLETE#<athlete_id>", Type="ATHLETE"
# Sessions: PK="ATHLETE#<athlete_id>", SK="SESSION#<session_id>", Type="SESSION"
# GSI: GSI1PK="SESSION", GSI1SK="<date>#<session_id>" for querying all sessions


def _get_table():
    """Get DynamoDB table instance."""
    table_name = os.environ.get("DYNAMODB_TABLE_NAME", "training-tracker")
    dynamodb = _get_dynamodb()
    return dynamodb.Table(table_name)


def get_all_sessions() -> Dict[str, TrainingSession]:
    """Get all training sessions."""
    table = _get_table()

    # Query GSI to get all sessions
    response = table.query(IndexName="GSI1", KeyConditionExpression=Key("GSI1PK").eq("SESSION"))

    sessions = {}
    for item in response.get("Items", []):
        session = _item_to_session(item)
        if session:
            sessions[session.id] = session

    return sessions


def get_session(session_id: str) -> TrainingSession | None:
    """Get a training session by ID."""
    table = _get_table()

    # Query GSI to find the session
    # Note: We query all sessions and filter in-memory since we don't know the date prefix
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq("SESSION"),
        FilterExpression=Attr("SessionId").eq(session_id),
    )

    items = response.get("Items", [])
    if not items:
        return None

    return _item_to_session(items[0])


def create_session(session: TrainingSession) -> None:
    """Create a new training session."""
    table = _get_table()

    table.put_item(
        Item={
            "PK": f"ATHLETE#{session.athlete_id}",
            "SK": f"SESSION#{session.id}",
            "GSI1PK": "SESSION",
            "GSI1SK": f"{session.date.isoformat()}#{session.id}",
            "Type": "SESSION",
            "SessionId": session.id,
            "AthleteId": session.athlete_id,
            "AthleteName": session.athlete_name,
            "Date": session.date.isoformat(),
            "Duration": str(session.duration),
            "Distance": str(session.distance),
            "Notes": session.notes or "",
            "CreatedAt": session.createdAt.isoformat(),
            "UpdatedAt": session.updatedAt.isoformat(),
        }
    )


def update_session(session: TrainingSession) -> None:
    """Update an existing training session."""
    table = _get_table()

    table.put_item(
        Item={
            "PK": f"ATHLETE#{session.athlete_id}",
            "SK": f"SESSION#{session.id}",
            "GSI1PK": "SESSION",
            "GSI1SK": f"{session.date.isoformat()}#{session.id}",
            "Type": "SESSION",
            "SessionId": session.id,
            "AthleteId": session.athlete_id,
            "AthleteName": session.athlete_name,
            "Date": session.date.isoformat(),
            "Duration": str(session.duration),
            "Distance": str(session.distance),
            "Notes": session.notes or "",
            "CreatedAt": session.createdAt.isoformat(),
            "UpdatedAt": session.updatedAt.isoformat(),
        }
    )


def delete_session(session_id: str) -> None:
    """Delete a training session."""
    # First find the session to get the athlete_id
    session = get_session(session_id)
    if not session:
        return

    table = _get_table()
    table.delete_item(Key={"PK": f"ATHLETE#{session.athlete_id}", "SK": f"SESSION#{session_id}"})


def session_exists(session_id: str) -> bool:
    """Check if a training session exists."""
    return get_session(session_id) is not None


# Athlete operations
def get_all_athletes() -> Dict[str, Athlete]:
    """Get all athletes."""
    table = _get_table()

    # Scan for all athlete items
    response = table.scan(FilterExpression=Attr("Type").eq("ATHLETE"))

    athletes = {}
    for item in response.get("Items", []):
        athlete = _item_to_athlete(item)
        if athlete:
            athletes[athlete.id] = athlete

    return athletes


def get_athlete(athlete_id: str) -> Athlete | None:
    """Get an athlete by ID."""
    table = _get_table()

    response = table.get_item(Key={"PK": f"ATHLETE#{athlete_id}", "SK": f"ATHLETE#{athlete_id}"})

    item = response.get("Item")
    if not item:
        return None

    return _item_to_athlete(item)


def create_athlete(athlete: Athlete) -> None:
    """Create a new athlete."""
    table = _get_table()

    table.put_item(
        Item={
            "PK": f"ATHLETE#{athlete.id}",
            "SK": f"ATHLETE#{athlete.id}",
            "Type": "ATHLETE",
            "AthleteId": athlete.id,
            "Name": athlete.name,
        }
    )


def update_athlete(athlete: Athlete) -> None:
    """Update an existing athlete."""
    table = _get_table()

    table.put_item(
        Item={
            "PK": f"ATHLETE#{athlete.id}",
            "SK": f"ATHLETE#{athlete.id}",
            "Type": "ATHLETE",
            "AthleteId": athlete.id,
            "Name": athlete.name,
        }
    )


def delete_athlete(athlete_id: str) -> None:
    """Delete an athlete."""
    table = _get_table()

    table.delete_item(Key={"PK": f"ATHLETE#{athlete_id}", "SK": f"ATHLETE#{athlete_id}"})


def athlete_exists(athlete_id: str) -> bool:
    """Check if an athlete exists."""
    return get_athlete(athlete_id) is not None


def get_sessions_by_athlete(athlete_id: str) -> list[TrainingSession]:
    """Get all training sessions for a specific athlete."""
    table = _get_table()

    # Query all sessions for this athlete
    response = table.query(
        KeyConditionExpression=Key("PK").eq(f"ATHLETE#{athlete_id}") & Key("SK").begins_with("SESSION#")
    )

    sessions = []
    for item in response.get("Items", []):
        session = _item_to_session(item)
        if session:
            sessions.append(session)

    return sessions


def count_sessions_by_athlete(athlete_id: str) -> int:
    """Count training sessions for a specific athlete."""
    return len(get_sessions_by_athlete(athlete_id))


def delete_sessions_by_athlete(athlete_id: str) -> int:
    """Delete all training sessions for a specific athlete. Returns count of deleted sessions."""
    table = _get_table()
    sessions = get_sessions_by_athlete(athlete_id)

    # Batch delete sessions
    with table.batch_writer() as batch:
        for session in sessions:
            batch.delete_item(Key={"PK": f"ATHLETE#{athlete_id}", "SK": f"SESSION#{session.id}"})

    return len(sessions)


def _item_to_athlete(item: dict) -> Athlete | None:
    """Convert DynamoDB item to Athlete model."""
    try:
        return Athlete(
            id=item["AthleteId"],
            name=item["Name"],
        )
    except (KeyError, ValueError):
        return None


def _item_to_session(item: dict) -> TrainingSession | None:
    """Convert DynamoDB item to TrainingSession model."""
    try:
        return TrainingSession(
            id=item["SessionId"],
            athlete_id=item["AthleteId"],
            athlete_name=item["AthleteName"],
            date=datetime.date.fromisoformat(item["Date"]),
            duration=float(item["Duration"]),
            distance=float(item["Distance"]),
            notes=item.get("Notes") or None,
            createdAt=datetime.datetime.fromisoformat(item["CreatedAt"]),
            updatedAt=datetime.datetime.fromisoformat(item["UpdatedAt"]),
        )
    except (KeyError, ValueError):
        return None


def initialize_example_data() -> None:
    """Initialize storage with example athletes and training sessions."""
    # Create example athletes
    example_athletes = [
        Athlete(id="athlete-1", name="John Doe"),
        Athlete(id="athlete-2", name="Jane Smith"),
    ]

    for athlete in example_athletes:
        create_athlete(athlete)

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
        create_session(session)
