"""Unit tests for the Training Tracker API."""


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Training Sessions API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"


class TestCreateTrainingSession:
    """Tests for creating training sessions."""

    def test_create_session_success(self, client, sample_session_data):
        """Test creating a training session successfully."""
        response = client.post("/v1/training-sessions", json=sample_session_data)
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == sample_session_data["date"]
        assert data["duration"] == sample_session_data["duration"]
        assert data["distance"] == sample_session_data["distance"]
        assert data["notes"] == sample_session_data["notes"]
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_session_without_notes(self, client, test_athlete):
        """Test creating a session without optional notes field."""
        data = {"athlete_id": test_athlete.id, "date": "2025-10-23", "duration": 30.0, "distance": 5.0}
        response = client.post("/v1/training-sessions", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["notes"] is None

    def test_create_session_negative_duration(self, client, test_athlete):
        """Test creating a session with negative duration fails."""
        data = {"athlete_id": test_athlete.id, "date": "2025-10-23", "duration": -10.0, "distance": 5.0}
        response = client.post("/v1/training-sessions", json=data)
        assert response.status_code == 422

    def test_create_session_negative_distance(self, client, test_athlete):
        """Test creating a session with negative distance fails."""
        data = {"athlete_id": test_athlete.id, "date": "2025-10-23", "duration": 30.0, "distance": -5.0}
        response = client.post("/v1/training-sessions", json=data)
        assert response.status_code == 422

    def test_create_session_missing_required_fields(self, client):
        """Test creating a session without required fields fails."""
        response = client.post("/v1/training-sessions", json={"date": "2025-10-23"})
        assert response.status_code == 422


class TestListTrainingSessions:
    """Tests for listing training sessions."""

    def test_list_empty_sessions(self, client):
        """Test listing sessions when database is empty."""
        response = client.get("/v1/training-sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_list_sessions(self, client, test_athlete, sample_session_data):
        """Test listing sessions returns all sessions."""
        # Create multiple sessions
        client.post("/v1/training-sessions", json=sample_session_data)
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-24", "duration": 60.0, "distance": 12.0},
        )

        response = client.get("/v1/training-sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 2
        assert data["pagination"]["hasMore"] is False

    def test_list_sessions_with_date_filter(self, client, test_athlete):
        """Test listing sessions with date range filtering."""
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-20", "duration": 30.0, "distance": 5.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-25", "duration": 45.0, "distance": 8.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-30", "duration": 60.0, "distance": 12.0},
        )

        response = client.get("/v1/training-sessions?startDate=2025-10-24&endDate=2025-10-28")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["date"] == "2025-10-25"

    def test_list_sessions_pagination(self, client, test_athlete):
        """Test listing sessions with pagination."""
        for i in range(5):
            client.post(
                "/v1/training-sessions",
                json={"athlete_id": test_athlete.id, "date": f"2025-10-{20 + i}", "duration": 30.0, "distance": 5.0},
            )

        response = client.get("/v1/training-sessions?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["hasMore"] is True

        response = client.get("/v1/training-sessions?limit=2&offset=4")
        data = response.json()
        assert len(data["data"]) == 1
        assert data["pagination"]["hasMore"] is False

    def test_list_sessions_sorted_by_date(self, client, test_athlete):
        """Test that sessions are sorted by date (most recent first)."""
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-20", "duration": 30.0, "distance": 5.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-25", "duration": 45.0, "distance": 8.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-22", "duration": 60.0, "distance": 12.0},
        )

        response = client.get("/v1/training-sessions")
        data = response.json()
        dates = [session["date"] for session in data["data"]]
        assert dates == ["2025-10-25", "2025-10-22", "2025-10-20"]


class TestGetTrainingSession:
    """Tests for getting a single training session."""

    def test_get_session_success(self, client, sample_session_data):
        """Test getting a session by ID."""
        create_response = client.post("/v1/training-sessions", json=sample_session_data)
        session_id = create_response.json()["id"]

        response = client.get(f"/v1/training-sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["date"] == sample_session_data["date"]

    def test_get_session_not_found(self, client):
        """Test getting a non-existent session returns 404."""
        response = client.get("/v1/training-sessions/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "NOT_FOUND"


class TestUpdateTrainingSession:
    """Tests for updating training sessions."""

    def test_update_session_success(self, client, test_athlete, sample_session_data):
        """Test updating a session successfully."""
        create_response = client.post("/v1/training-sessions", json=sample_session_data)
        session_id = create_response.json()["id"]
        created_at = create_response.json()["createdAt"]

        updated_data = {
            "athlete_id": test_athlete.id,
            "date": "2025-10-24",
            "duration": 50.0,
            "distance": 10.0,
            "notes": "Updated run",
        }

        response = client.put(f"/v1/training-sessions/{session_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["date"] == updated_data["date"]
        assert data["duration"] == updated_data["duration"]
        assert data["distance"] == updated_data["distance"]
        assert data["notes"] == updated_data["notes"]
        assert data["createdAt"] == created_at
        assert data["updatedAt"] != data["createdAt"]

    def test_update_session_not_found(self, client, sample_session_data):
        """Test updating a non-existent session returns 404."""
        response = client.put("/v1/training-sessions/nonexistent-id", json=sample_session_data)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "NOT_FOUND"

    def test_update_session_invalid_data(self, client, sample_session_data):
        """Test updating with invalid data fails."""
        create_response = client.post("/v1/training-sessions", json=sample_session_data)
        session_id = create_response.json()["id"]

        invalid_data = {"date": "2025-10-24", "duration": -10.0, "distance": 5.0}
        response = client.put(f"/v1/training-sessions/{session_id}", json=invalid_data)
        assert response.status_code == 422


class TestDeleteTrainingSession:
    """Tests for deleting training sessions."""

    def test_delete_session_success(self, client, sample_session_data):
        """Test deleting a session successfully."""
        create_response = client.post("/v1/training-sessions", json=sample_session_data)
        session_id = create_response.json()["id"]

        response = client.delete(f"/v1/training-sessions/{session_id}")
        assert response.status_code == 204

        # Verify session is deleted
        get_response = client.get(f"/v1/training-sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, client):
        """Test deleting a non-existent session returns 404."""
        response = client.delete("/v1/training-sessions/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "NOT_FOUND"


class TestStatistics:
    """Tests for training statistics endpoint."""

    def test_statistics_empty_database(self, client):
        """Test statistics with empty database."""
        response = client.get("/v1/training-sessions/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["totalSessions"] == 0
        assert data["totalDuration"] == 0.0
        assert data["totalDistance"] == 0.0
        assert data["averageDuration"] == 0.0
        assert data["averageDistance"] == 0.0
        assert data["averagePace"] == 0.0

    def test_statistics_single_session(self, client, test_athlete):
        """Test statistics with a single session."""
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-23", "duration": 50.0, "distance": 10.0},
        )

        response = client.get("/v1/training-sessions/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["totalSessions"] == 1
        assert data["totalDuration"] == 50.0
        assert data["totalDistance"] == 10.0
        assert data["averageDuration"] == 50.0
        assert data["averageDistance"] == 10.0
        assert data["averagePace"] == 5.0

    def test_statistics_multiple_sessions(self, client, test_athlete):
        """Test statistics with multiple sessions."""
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-20", "duration": 30.0, "distance": 5.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-21", "duration": 60.0, "distance": 10.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-22", "duration": 45.0, "distance": 9.0},
        )

        response = client.get("/v1/training-sessions/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["totalSessions"] == 3
        assert data["totalDuration"] == 135.0
        assert data["totalDistance"] == 24.0
        assert data["averageDuration"] == 45.0
        assert data["averageDistance"] == 8.0
        assert round(data["averagePace"], 2) == 5.62

    def test_statistics_with_date_filter(self, client, test_athlete):
        """Test statistics with date range filtering."""
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-20", "duration": 30.0, "distance": 5.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-25", "duration": 60.0, "distance": 10.0},
        )
        client.post(
            "/v1/training-sessions",
            json={"athlete_id": test_athlete.id, "date": "2025-10-30", "duration": 45.0, "distance": 9.0},
        )

        response = client.get("/v1/training-sessions/statistics?startDate=2025-10-24&endDate=2025-10-28")
        assert response.status_code == 200
        data = response.json()
        assert data["totalSessions"] == 1
        assert data["totalDuration"] == 60.0
        assert data["totalDistance"] == 10.0

    def test_statistics_zero_distance(self, client):
        """Test statistics calculation with zero total distance."""
        client.post("/v1/training-sessions", json={"date": "2025-10-20", "duration": 30.0, "distance": 0.0})

        response = client.get("/v1/training-sessions/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["averagePace"] == 0.0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_pagination_limit_boundaries(self, client):
        """Test pagination limit boundaries."""
        # Test minimum limit
        response = client.get("/v1/training-sessions?limit=1")
        assert response.status_code == 200

        # Test maximum limit
        response = client.get("/v1/training-sessions?limit=100")
        assert response.status_code == 200

        # Test exceeding maximum limit
        response = client.get("/v1/training-sessions?limit=101")
        assert response.status_code == 422

        # Test below minimum limit
        response = client.get("/v1/training-sessions?limit=0")
        assert response.status_code == 422

    def test_negative_offset(self, client):
        """Test negative offset is rejected."""
        response = client.get("/v1/training-sessions?offset=-1")
        assert response.status_code == 422

    def test_invalid_date_format(self, client):
        """Test invalid date format is rejected."""
        response = client.post(
            "/v1/training-sessions", json={"date": "invalid-date", "duration": 30.0, "distance": 5.0}
        )
        assert response.status_code == 422

    def test_notes_max_length(self, client):
        """Test notes field respects max length."""
        long_notes = "x" * 1001
        response = client.post(
            "/v1/training-sessions",
            json={"date": "2025-10-23", "duration": 30.0, "distance": 5.0, "notes": long_notes},
        )
        assert response.status_code == 422
