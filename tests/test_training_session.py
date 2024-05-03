import pytest
from training_tracker.training_session import TrainingSession


@pytest.mark.usefixtures("training_session_table")
def test_training_session_crud():
    training_session = TrainingSession(
        title="trainingSession 1", discipline="running", date="2021-01-01", distance=1000
    )
    training_session.save()
    training_session = TrainingSession.get(training_session.id)
    assert training_session.id
    assert training_session.title == "trainingSession 1"
    assert training_session.discipline == "running"
    assert training_session.date == "2021-01-01"
    assert training_session.distance == 1000
    assert training_session.version != "1"

    assert TrainingSession.count() == 1
    training_session.delete()
    assert TrainingSession.count() == 0
