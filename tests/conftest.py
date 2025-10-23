"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from training_tracker.main import app
from training_tracker.models import Athlete
from training_tracker.storage import athletes_db, training_sessions_db


@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test."""
    training_sessions_db.clear()
    athletes_db.clear()
    yield
    training_sessions_db.clear()
    athletes_db.clear()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_athlete():
    """Provide a test athlete."""
    athlete = Athlete(id="test-athlete-1", name="Test Athlete")
    athletes_db[athlete.id] = athlete
    return athlete


@pytest.fixture
def sample_session_data(test_athlete):
    """Sample training session data for testing."""
    return {
        "athlete_id": test_athlete.id,
        "date": "2025-10-23",
        "duration": 45.5,
        "distance": 8.5,
        "notes": "Morning run with intervals",
    }
