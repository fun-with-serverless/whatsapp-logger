import moto  # type: ignore
import boto3
import pytest
import base64
import os
from src.utils.dynamodb_models import ApplicationState

SECRET_STRING = "password"
SECRET_GOOGLE_AUTH = "google auth"
USER = "admin"
MOCK_SHEET_URL = "https://google_sheet.com"


@pytest.fixture
def s3(monkeypatch):
    with moto.mock_s3():
        # set up the mock S3 environment
        conn = boto3.client("s3")
        conn.create_bucket(Bucket="bucket")
        conn.put_object(Bucket="bucket", Key="qr.jpg", Body="test")

        monkeypatch.setenv("QR_BUCKET_NAME", "bucket")
        monkeypatch.setenv("QR_FILE_PATH", "qr.jpg")
        yield conn


@pytest.fixture
def secret_manager(monkeypatch):
    with moto.mock_secretsmanager():
        client = boto3.client("secretsmanager")

        # Create a secret in Secrets Manager
        secret_name = "secret"
        google_secret_auth_name = "google_secret_auth_name"

        client.create_secret(Name=secret_name, SecretString=SECRET_STRING)
        client.create_secret(
            Name=google_secret_auth_name, SecretString=SECRET_GOOGLE_AUTH
        )

        monkeypatch.setenv("LOGIN_USER", "admin")
        monkeypatch.setenv("SECRETAUTH_PARAM_NAME", secret_name)
        monkeypatch.setenv("GOOGLE_SECRET_AUTH_NAME", google_secret_auth_name)

        yield client


@pytest.fixture
def parameters_store(monkeypatch):
    with moto.mock_ssm():
        client = boto3.client("ssm")

        param_name = "google_sheet"
        client.put_parameter(
            Name=param_name, Value=MOCK_SHEET_URL, Type="String", Overwrite=True
        )

        monkeypatch.setenv("GOOGLE_SHEET_URL", param_name)

        yield client


@pytest.fixture
def application_state_db(monkeypatch):
    with moto.mock_dynamodb():
        ApplicationState.create_table(wait=True)
        yield


@pytest.fixture
def basic_auth() -> str:
    basic_auth = base64.b64encode(f"{USER}:{SECRET_STRING}".encode()).decode()
    return f"Basic {basic_auth}"


@pytest.fixture(autouse=True)
def set_aws_region():
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    yield
    del os.environ["AWS_DEFAULT_REGION"]
