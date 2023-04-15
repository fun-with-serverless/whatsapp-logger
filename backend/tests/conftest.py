from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import moto  # type: ignore
import boto3
import pytest
import base64
import os
import json
from backend.src.chatgpt_integration.utils.consts import SUMMARY_PREFIX
from backend.src.utils.db_models.application_state import ApplicationState
from backend.src.utils.db_models.whatsapp_groups import WhatsAppGroup
from backend.src.utils.models import WhatsAppMessage

SECRET_STRING = "password"
SECRET_GOOGLE_AUTH = "google auth"
OPENAI_KEY = "!@#$%"
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
        openai_secret = "openai_secret"

        client.create_secret(Name=secret_name, SecretString=SECRET_STRING)
        client.create_secret(
            Name=google_secret_auth_name, SecretString=SECRET_GOOGLE_AUTH
        )
        client.create_secret(Name=openai_secret, SecretString=OPENAI_KEY)

        monkeypatch.setenv("LOGIN_USER", "admin")
        monkeypatch.setenv("SECRETAUTH_PARAM_NAME", secret_name)
        monkeypatch.setenv("GOOGLE_SECRET_AUTH_NAME", google_secret_auth_name)
        monkeypatch.setenv("OPENAI_KEY", openai_secret)

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
def group_db(monkeypatch):
    with moto.mock_dynamodb():
        WhatsAppGroup.create_table(wait=True)
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


@pytest.fixture
def bucket_name_env(monkeypatch):
    name = "bucket"
    monkeypatch.setenv("CHATS_BUCKET", name)
    yield name


@pytest.fixture
def events(monkeypatch):
    with moto.mock_events():
        with moto.mock_sqs():
            monkeypatch.setenv("EVENT_BUS_ARN", "EventBus")
            events_client = boto3.client("events")
            events_client.create_event_bus(Name="EventBus")

            events_client.put_rule(
                Name="MyNewRule",
                EventPattern=json.dumps(
                    {
                        "source": ["admin", "chatgpt"],
                        "detail-type": ["logout", "summary"],
                    }
                ),
                State="ENABLED",
                EventBusName="EventBus",
            )

            sqs_client = boto3.client("sqs")

            queue_url = sqs_client.create_queue(QueueName="MyNewQueue")["QueueUrl"]

            queue_arn = sqs_client.get_queue_attributes(
                QueueUrl=queue_url, AttributeNames=["QueueArn"]
            )["Attributes"]["QueueArn"]
            events_client.put_targets(
                Rule="MyNewRule", Targets=[{"Id": "MyNewTarget", "Arn": queue_arn}]
            )

            yield queue_url


@pytest.fixture
def s3_chats(bucket_name_env):
    with moto.mock_s3():
        # set up the mock S3 environment
        conn = boto3.client("s3")
        conn.create_bucket(Bucket=bucket_name_env)

        file_name = f"{SUMMARY_PREFIX}/random_file1.json"
        conn.put_object(
            Bucket=bucket_name_env,
            Key=file_name,
            Body=f"{json.dumps({'group_name': 'gorup-name', 'group_id': 'group-id', 'chats': 'result is' })}",
        )

        yield conn, file_name


@pytest.fixture
def s3_raw_lake(bucket_name_env, request):
    def to_epoch(val: datetime) -> int:
        return int(val.timestamp())

    with moto.mock_s3():
        # set up the mock S3 environment
        conn = boto3.client("s3")
        conn.create_bucket(Bucket=bucket_name_env)
        data_date = request.node.get_closest_marker("data_date")
        date = datetime.now(tz=timezone.utc) - timedelta(days=1)
        if data_date is not None:
            date = data_date.args[0]

        message1 = WhatsAppMessage(
            "test",
            "group-id",
            datetime(year=2023, month=1, day=10, hour=23, minute=23),
            "Hello",
            "participant-id",
            participant_handle="Efi",
            participant_number="123456",
            has_media=False,
        )

        message2 = WhatsAppMessage(
            "test",
            "group-id",
            datetime(year=2023, month=1, day=10, hour=23, minute=24),
            "Hi",
            "participant-id",
            participant_handle="Efi",
            participant_number="123456",
            has_media=False,
            quoted_message="Hello",
            quoted_message_participant_contact_name=None,
            quoted_message_participant_handle="Anat",
        )

        conn.put_object(
            Bucket=bucket_name_env,
            Key=f"{date.strftime('%Y.%m.%d')}/random_file1",
            Body=f"{json.dumps(asdict(message1), default=to_epoch)}\n",
        )

        conn.put_object(
            Bucket=bucket_name_env,
            Key=f"{date.strftime('%Y.%m.%d')}/random_file2",
            Body=f"{json.dumps(asdict(message2), default=to_epoch)}\n",
        )

        yield conn
