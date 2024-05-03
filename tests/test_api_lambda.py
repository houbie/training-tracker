from unittest.mock import Mock

import pytest
from training_tracker.api_lambda import handler


@pytest.mark.usefixtures("training_session_table")
def test_handler():
    event = {
        "requestContext": {},
        "resource": "/{proxy+}",
        "path": "/api/training-session",
        "pathParameters": {"proxy": "training-session"},
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {},
        "isBase64Encoded": False,
        "body": None,
    }

    assert handler(event, Mock()) == {
        "statusCode": 200,
        "body": "[]",
        "headers": {"content-length": "2", "content-type": "application/json"},
        "isBase64Encoded": False,
        "multiValueHeaders": {},
    }
