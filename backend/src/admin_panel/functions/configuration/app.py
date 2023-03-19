from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import (
    LambdaFunctionUrlResolver,
    Response,
    CORSConfig,
)

from dacite import from_dict

from ....utils.client import Client, DetailType, Source


from ....utils.db_models.whatsapp_groups import (
    SummaryStatus,
    WhatsAppGroup,
    SummaryLanguage,
)

from ....utils.authentication import basic_authenticate
from ....utils.db_models.application_state import ApplicationState, ClientStatus
from aws_lambda_powertools.utilities import parameters
import boto3


import os
import functools
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Configuration:
    google_secret: str
    sheet_url: str
    openai_key: str


@dataclass(frozen=True)
class Status:
    device_status: str
    last_message_arrived: int
    total_today: int


@dataclass(frozen=True)
class AdminPanelWhatsAppGroup:
    group_id: str
    name: str
    mute: bool
    summary_status: SummaryStatus
    summary_language: SummaryLanguage


def enum_serializer(obj) -> str:
    def enum_to_str(val) -> str:
        return val.value

    return json.dumps(obj, default=enum_to_str)


logger = Logger()
app = LambdaFunctionUrlResolver(
    CORSConfig(allow_origin="*"),
    serializer=enum_serializer,
)


@app.get("/device-status")
@basic_authenticate(app)
def get_device_status():
    status = ClientStatus.DISCONNECTED.value
    try:
        status = ApplicationState.get_client_status().value
    except ApplicationState.DoesNotExist:
        pass
    statistics = ApplicationState.get_message_statistics()
    return asdict(
        Status(
            device_status=status,
            last_message_arrived=int(
                statistics.last_message_arrived.timestamp() * 1000
            ),
            total_today=statistics.total_today,
        )
    )


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
            openai_key=parameters.get_secret(os.environ["OPENAI_KEY"]),
        )
    )


@app.get("/groups")
@basic_authenticate(app)
def get_groups():
    results = WhatsAppGroup.scan()
    return_value = [
        asdict(
            AdminPanelWhatsAppGroup(
                group_id=result.id,
                name=result.name,
                mute=result.always_mark_read,
                summary_status=result.requires_daily_summary,
                summary_language=result.summary_language,
            )
        )
        for result in results
    ]

    return {"groups": return_value}


@app.put("/groups/<group_id>")
@basic_authenticate(app)
def update_group(group_id: str):
    if app.current_event.body is None:
        return Response(502)
    try:
        group = WhatsAppGroup.get(group_id)
        update_details = json.loads(app.current_event.body)
        if "summary_status" in update_details:
            group.update(
                actions=[
                    WhatsAppGroup.requires_daily_summary.set(
                        SummaryStatus.from_str(update_details["summary_status"])
                    )
                ]
            )
        if "summary_language" in update_details:
            group.update(
                actions=[
                    WhatsAppGroup.summary_language.set(
                        SummaryLanguage.from_str(update_details["summary_language"])
                    )
                ]
            )
    except WhatsAppGroup.DoesNotExist:
        return Response(404)


@app.post("/configuration")
@basic_authenticate(app)
def set_configuratio():
    conf = from_dict(data_class=Configuration, data=json.loads(app.current_event.body))
    secret = _get_secret_manager()
    secret.update_secret(
        SecretId=os.environ["GOOGLE_SECRET_AUTH_NAME"],
        SecretString=conf.google_secret if conf.google_secret else "Replace",
    )
    secret.update_secret(
        SecretId=os.environ["OPENAI_KEY"],
        SecretString=conf.openai_key if conf.openai_key else "Replace",
    )
    ssm = _get_ssm()
    ssm.put_parameter(
        Name=os.environ["GOOGLE_SHEET_URL"],
        Value=conf.sheet_url if conf.sheet_url else "Replace",
        Type="String",
        Overwrite=True,
    )
    return Response(status_code=200)


@app.post("/disconnect")
@basic_authenticate(app)
def disconnect():
    client = Client()
    client.send_message(detail_type=DetailType.LOGOUT, source=Source.ADMIN, detail={})
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


def _get_qr_image() -> bytes:
    bucket_name = os.environ["QR_BUCKET_NAME"]
    file_path = os.environ["QR_FILE_PATH"]
    return _get_s3().get_object(Bucket=bucket_name, Key=file_path)["Body"].read()
