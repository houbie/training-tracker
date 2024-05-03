from pathlib import Path

from aws_lambda_powertools.logging import Logger

from training_tracker.application_factory import create_app, create_handler

logger = Logger()

specification_dir = Path(__file__).parent
while not (specification_dir / "OpenAPI.yaml").exists():
    specification_dir = specification_dir.parent
    if specification_dir == Path("/"):
        raise FileNotFoundError("OpenAPI.yaml not found")

app = create_app(
    "test",
    "OpenAPI.yaml",
    specification_dir=specification_dir,
    base_path="/api",
)
_handler = create_handler(app)


def handler(event, context):
    logger.info("Delegating %s to connexion app", event["path"])
    return _handler(event, context)
