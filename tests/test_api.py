import pytest

from .assertion_utils import assert_similar


@pytest.mark.usefixtures("training_session_table")
def test_training_session_crud(api_client):
    training_session = {
        "title": "training-session-title",
        "discipline": "cycling",
        "date": "2024-04-30",
        "distance": 5000,
    }

    response = api_client.post("api/training-session", json=training_session)
    assert response.status_code == 200
    created_training_session = response.json()
    assert created_training_session["title"] == "training-session-title"
    assert created_training_session["discipline"] == "cycling"
    assert created_training_session["date"] == "2024-04-30"
    assert created_training_session["distance"] == 5000
    assert created_training_session["version"] == 1

    response = api_client.get(f"api/training-session/{created_training_session['id']}")
    assert response.status_code == 200
    assert response.json() == created_training_session
    assert api_client.get("api/training-session").json() == [created_training_session]

    new_training_session = {
        "title": "new-training-session-title",
        "discipline": "swimming",
        "date": "2024-05-01",
        "distance": 3000,
        "version": 1,
    }
    response = api_client.put(f"api/training-session/{created_training_session['id']}", json=new_training_session)
    assert response.status_code == 200
    assert_similar(
        response.json(),
        {
            **new_training_session,
            "version": 2,
        },
    )
    assert_similar(
        api_client.get(f"api/training-session/{created_training_session["id"]}").json(),
        {
            **new_training_session,
            "version": 2,
        },
    )

    assert api_client.delete(f"api/training-session/{created_training_session['id']}").status_code == 204
    assert api_client.get("api/training-session/training_session-id").status_code == 404
    assert api_client.get("api/training-session").json() == []


@pytest.mark.usefixtures("training_session_table")
def test_validation(api_client):
    response = api_client.post("api/training-session", json={})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "'title' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }

    response = api_client.post("api/training-session", json={"title": "training-session-title"})
    assert response.json() == {
        "detail": "'discipline' is a required property",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }

    response = api_client.post(
        "api/training-session", json={"title": "training-session-title", "discipline": "running", "date": "2023-02-29"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "'2023-02-29' is not a 'date' - 'date'",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }
    response = api_client.post(
        "api/training-session", json={"title": "training-session-title", "discipline": "running", "date": "2023-1-1"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "'2023-1-1' is not a 'date' - 'date'",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }
