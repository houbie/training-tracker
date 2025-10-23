"""Pytest configuration and shared fixtures."""

import os

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from training_tracker.database import create_athlete
from training_tracker.main import app
from training_tracker.models import Athlete


def mock_aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["DYNAMODB_TABLE_NAME"] = "training-tracker-test"


def init_dynamodb():
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")

    # Create table
    dynamodb.create_table(
        TableName="training-tracker-test",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )
    return dynamodb


@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    mock_aws_credentials()


@pytest.fixture(scope="function", autouse=True)
def dynamodb_table(aws_credentials):
    """Create a mocked DynamoDB table for tests."""
    with mock_aws():
        # Create DynamoDB client
        # Keep the mock active for the entire test
        yield init_dynamodb()


@pytest.fixture
def client(dynamodb_table):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_athlete(dynamodb_table):
    """Provide a test athlete."""

    athlete = Athlete(id="test-athlete-1", name="Test Athlete")
    create_athlete(athlete)
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
