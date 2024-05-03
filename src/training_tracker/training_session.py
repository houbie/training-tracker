import uuid
from datetime import timedelta

from pynamodb.attributes import NumberAttribute, TTLAttribute, UnicodeAttribute, VersionAttribute
from pynamodb.models import Model

# ruff: noqa: N815


def generate_id():
    return str(uuid.uuid4())


class TrainingSession(Model):
    """A simple Task model."""

    class Meta:
        table_name = "task"

    id = UnicodeAttribute(hash_key=True, default=generate_id)
    title = UnicodeAttribute()
    discipline = UnicodeAttribute()
    date = UnicodeAttribute(null=True)
    distance = NumberAttribute(null=True)
    expirationDate = TTLAttribute(default=timedelta(hours=1))  # type: ignore
    version = VersionAttribute()
