import os
import uuid
from datetime import timedelta

from pynamodb.attributes import NumberAttribute, TTLAttribute, UnicodeAttribute, VersionAttribute
from pynamodb.models import Model

# ruff: noqa: N815

DYNAMODB_HOST = os.environ.get("DYNAMODB_HOST")
REGION = os.environ.get("AWS_REGION", "eu-west-1")
TABLE_NAME = os.environ.get("TRAINING_SESSIONS_TABLE", "user")


def generate_id():
    return str(uuid.uuid4())


class TrainingSession(Model):
    """A simple Task model."""

    class Meta:
        host = DYNAMODB_HOST
        region = REGION
        table_name = TABLE_NAME

    id = UnicodeAttribute(hash_key=True, default=generate_id)
    title = UnicodeAttribute()
    discipline = UnicodeAttribute()
    date = UnicodeAttribute(null=True)
    distance = NumberAttribute(null=True)
    expirationDate = TTLAttribute(default=timedelta(hours=1))  # type: ignore
    version = VersionAttribute()
