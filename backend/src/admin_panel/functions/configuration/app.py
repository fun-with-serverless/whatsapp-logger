from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver, Response
from dacite import from_dict

from ...utils.authentication import basic_authenticate
from ...utils.dynamodb_models import ApplicationState, ClientStatus
from aws_lambda_powertools.utilities import parameters
import boto3


import os
import functools
import json
from dataclasses import dataclass, asdict

logger = Logger()
app = LambdaFunctionUrlResolver()


@dataclass(frozen=True)
class Configuration:
    google_secret: str
    sheet_url: str


@dataclass(frozen=True)
class DeviceStatus:
    device_status: str


@app.get("/device-status")
@basic_authenticate(app)
def get_device_status():
    status = ClientStatus.DISCONNECTED.value
    try:
        status = ApplicationState.get_client_status().value
    except ApplicationState.DoesNotExist:
        pass
    return asdict(DeviceStatus(device_status=status))


@app.get("/qr-code")
@basic_authenticate(app)
def get_qr_code():
    return Response(status_code=200, content_type="image/png", body=_get_qr_image())


@app.get("/configuration")
@basic_authenticate(app)
def get_configuratio():
    return asdict(
        Configuration(
            google_secret=parameters.get_secret(os.environ["GOOGLE_SECRET_AUTH_NAME"]),
            sheet_url=parameters.get_parameter(os.environ["GOOGLE_SHEET_URL"]),
        )
    )


@app.get("/")
@basic_authenticate(app)
def home():
    return Response(status_code=200)


@app.post("/configuration")
@basic_authenticate(app)
def set_configuratio():
    conf = from_dict(data_class=Configuration, data=json.loads(app.current_event.body))
    secret = _get_secret_manager()
    secret.update_secret(
        SecretId=os.environ["GOOGLE_SECRET_AUTH_NAME"], SecretString=conf.google_secret
    )
    ssm = _get_ssm()
    ssm.put_parameter(
        Name=os.environ["GOOGLE_SHEET_URL"],
        Value=conf.sheet_url,
        Type="String",
        Overwrite=True,
    )
    return Response(status_code=200)


@app.post("/disconnect")
@basic_authenticate(app)
def disconnect():
    events = _get_events()
    events.put_events(
        Entries=[
            {
                "EventBusName": os.environ["EVENT_BUS_ARN"],
                "Detail": str({}),
                "DetailType": "logout",
                "Source": "admin",
            }
        ]
    )
    return Response(status_code=200)


@logger.inject_lambda_context(log_event=True)
def handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)


@functools.cache
def _get_s3():
    return boto3.client("s3")


@functools.cache
def _get_secret_manager():
    return boto3.client("secretsmanager")


@functools.cache
def _get_ssm():
    return boto3.client("ssm")


@functools.cache
def _get_events():
    return boto3.client("events")


def _get_qr_image() -> bytes:
    bucket_name = os.environ["QR_BUCKET_NAME"]
    file_path = os.environ["QR_FILE_PATH"]
    return _get_s3().get_object(Bucket=bucket_name, Key=file_path)["Body"].read()
