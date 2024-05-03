import os
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
from pytest_dynamodb import factories, plugin

DYNAMODB_DOWNLOAD_URL = "https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"


def download_dynamodb_local(target_dir):
    local_filename = Path(DYNAMODB_DOWNLOAD_URL.split("/", maxsplit=1)[0])
    with requests.get(DYNAMODB_DOWNLOAD_URL, stream=True, timeout=10) as resp, local_filename.open("wb") as file:
        for chunk in resp.iter_content(chunk_size=8192):
            file.write(chunk)
    with tarfile.open(local_filename, "r:gz") as tar:
        tar.extractall(path=target_dir)  # noqa: S202
    local_filename.unlink()
    print(f"downloaded local dynamodb to {target_dir}")


def prepare_dynamodb_local(download_dir: Path) -> None:
    print("downloadeding?")

    if not download_dir.joinpath("DynamoDBLocal.jar").exists():
        print("downloading...")
        download_dynamodb_local(download_dir)

    if os.environ.get("CUSTOM_DYNAMODB_PORT"):

        @pytest.fixture(scope="session")
        def external_dynamodb_proc_fixture():
            return SimpleNamespace(host="localhost", port=os.environ.get("CUSTOM_DYNAMODB_PORT", "9999"))

        plugin.dynamodb_proc = external_dynamodb_proc_fixture
    else:
        plugin.dynamodb_proc = factories.dynamodb_proc(str(download_dir))
