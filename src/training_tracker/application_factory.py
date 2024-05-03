import json
from datetime import datetime
from pathlib import Path

import orjson
from aws_lambda_powertools.logging import Logger
from connexion import AsyncApp
from connexion.jsonifier import Jsonifier
from connexion.lifecycle import ConnexionRequest, ConnexionResponse
from connexion.middleware import MiddlewarePosition
from jsonschema import draft4_format_checker
from mangum import Mangum
from mangum.adapter import DEFAULT_TEXT_MIME_TYPES
from pynamodb.exceptions import DoesNotExist, PynamoDBConnectionError
from starlette.middleware.cors import CORSMiddleware

logger = Logger()


class OrJsonifier(Jsonifier):
    """A Jsonifier that uses orjson for serialization and deserialization."""

    def dumps(self, data, **_kwargs):
        return orjson.dumps(data).decode()


@draft4_format_checker.checks("date")
def is_date(val):
    if not isinstance(val, str):
        return True
    if len(val) != 10:
        return False
    try:
        return datetime.strptime(val, "%Y-%m-%d")  # noqa: DTZ007
    except ValueError:
        return False


def pynamo_connection_error_handler(_request: ConnexionRequest, exc: PynamoDBConnectionError) -> ConnexionResponse:
    if exc.cause_response_code == "ConditionalCheckFailedException":
        return ConnexionResponse(
            status_code=409,
            body=json.dumps(
                {
                    "type": "CONFLICT",
                    "title": exc.cause_response_code,
                    "detail": exc.cause_response_message,
                    "status": 409,
                }
            ),
        )

    logger.error(exc)
    return ConnexionResponse(
        status_code=500,
        body=json.dumps(
            {
                "type": "INTERNAL_SERVER_ERROR",
                "detail": "Something went wrong. Check the logs for more information",
                "exception": str(exc),
                "status": 500,
                "title": "INTERNAL_SERVER_ERROR",
            }
        ),
    )


def pynamo_not_found_error_handler(_request: ConnexionRequest, _exc: Exception) -> ConnexionResponse:
    return ConnexionResponse(
        status_code=404,
        body=json.dumps(
            {
                "type": "RECORD_NOT_FOUND",
                "title": "The records does not exist",
                "status": 404,
            }
        ),
    )


def create_app(
    name: str,
    specification: str,
    specification_dir: Path,
    base_path: str | None = None,
) -> AsyncApp:
    """Create a connexion app."""
    connexion_app = AsyncApp(name, specification_dir=specification_dir, jsonifier=OrJsonifier())
    connexion_app.add_api(specification, base_path=base_path, pythonic_params=True, resolver_error=404)
    connexion_app.add_error_handler(PynamoDBConnectionError, pynamo_connection_error_handler)
    connexion_app.add_error_handler(DoesNotExist, pynamo_not_found_error_handler)
    connexion_app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return connexion_app


def create_handler(app: AsyncApp) -> Mangum:
    """Create a lambda handler for the app."""
    validation_errors_mime_type = "application/problem+json"
    return Mangum(app, lifespan="off", text_mime_types=[*DEFAULT_TEXT_MIME_TYPES, validation_errors_mime_type])
