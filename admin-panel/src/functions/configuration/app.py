from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import LambdaFunctionUrlResolver, Response
from dacite import from_dict

from src.utils.authentication import basic_authenticate
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
    print(conf)
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


@logger.inject_lambda_context
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


def _get_qr_image() -> bytes:
    bucket_name = os.environ["QR_BUCKET_NAME"]
    file_path = os.environ["QR_FILE_PATH"]
    return _get_s3().get_object(Bucket=bucket_name, Key=file_path)["Body"].read()
