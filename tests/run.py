from pathlib import Path

import uvicorn
from mirakuru import TCPExecutor
from port_for import get_port
from training_tracker.training_session import TrainingSession

path_dynamodb_jar = Path(__file__).parents[1].joinpath(".dynamodb/DynamoDBLocal.jar")
port = get_port(None)
dynamo_url = f"http://localhost:{port}"

dynamodb_executor = TCPExecutor(
    f"""java
        -Djava.library.path=./DynamoDBLocal_lib
        -jar {path_dynamodb_jar}
        -inMemory
        -port {port}""",
    host="localhost",
    port=port,
    timeout=60,
)
dynamodb_executor.start()

TrainingSession.Meta.host = dynamo_url
TrainingSession.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)


if __name__ == "__main__":
    uvicorn.run(
        app="training_tracker.api_lambda:app",
        port=8000,
        reload=True,
    )
