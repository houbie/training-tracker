from pathlib import Path

import pytest
from training_tracker import application_factory
from training_tracker.training_session import TrainingSession

from tests.dynamodb_local import prepare_dynamodb_local

prepare_dynamodb_local(Path(__file__).parent / "../.dynamodb")


@pytest.fixture()
def api_client():
    app = application_factory.create_app(
        "test",
        "openApi.yaml",
        Path(__file__).parent.parent,
        base_path="/api",
    )
    return app.test_client()


@pytest.fixture()
def training_session_table(dynamodb):
    TrainingSession.Meta.host = dynamodb.meta.client.meta.endpoint_url
    TrainingSession.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    yield dynamodb
    TrainingSession.delete_table()
