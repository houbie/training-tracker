from tests import conftest

conftest.mock_aws_credentials()

import uvicorn
from moto import mock_aws

from training_tracker.main import app


def main():
    aws = mock_aws()
    aws.start()
    conftest.init_dynamodb()
    uvicorn.run(app, host="0.0.0.0", port=8080)
    aws.stop()


if __name__ == "__main__":
    main()
