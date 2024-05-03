from training_tracker.training_session import TrainingSession, generate_id


def get_training_sessions():
    return [t.attribute_values for t in TrainingSession.scan()]


def create_training_session(body):
    training_session = TrainingSession(generate_id(), **body)
    training_session.save()
    return training_session.attribute_values


def get_training_session(training_session_id):
    return TrainingSession.get(training_session_id).attribute_values


def save_training_session(training_session_id, body: dict):
    body.pop("expirationDate", None)
    training_session = TrainingSession(training_session_id, **body)
    training_session.save()
    return training_session.attribute_values


def delete_training_session(training_session_id):
    training_session = TrainingSession.get(training_session_id)
    training_session.delete()
    return f"The trainingSession with id {training_session_id} has been deleted", 204
