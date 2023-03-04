from ...src.admin_panel.functions.configuration.app import handler
from unittest.mock import MagicMock
import json
from aws_lambda_powertools.utilities import parameters
import os
import boto3
from .utils import http_request
from ..conftest import OPENAI_KEY, SECRET_GOOGLE_AUTH, MOCK_SHEET_URL
from backend.src.utils.dynamodb_models import ApplicationState, ClientStatus


def test_get_configuration(secret_manager, parameters_store, basic_auth):
    request = http_request(path="/configuration")
    request["headers"]["Authorization"] = basic_auth

    response = handler(request, MagicMock())

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "google_secret": SECRET_GOOGLE_AUTH,
        "sheet_url": MOCK_SHEET_URL,
        "openai_key": OPENAI_KEY,
    }


def test_post_configuration(secret_manager, parameters_store, basic_auth):
    request = http_request(
        path="/configuration",
        method="POST",
        body=json.dumps(
            {
                "google_secret": "new auth",
                "sheet_url": "new url",
                "openai_key": "!Q!W@E#",
            }
        ),
    )
    request["headers"]["Authorization"] = basic_auth

    response = handler(request, MagicMock())

    assert response["statusCode"] == 200

    assert (
        parameters.get_secret(os.environ["GOOGLE_SECRET_AUTH_NAME"], force_fetch=True)
        == "new auth"
    )
    assert (
        parameters.get_parameter(os.environ["GOOGLE_SHEET_URL"], force_fetch=True)
        == "new url"
    )
    assert (
        parameters.get_secret(os.environ["OPENAI_KEY"], force_fetch=True) == "!Q!W@E#"
    )


def test_get_device_status(basic_auth, application_state_db, secret_manager):
    request = http_request(path="/device-status", method="GET")

    request["headers"]["Authorization"] = basic_auth

    ApplicationState.update_client_status(ClientStatus.DISCONNECTED)

    response = handler(request, MagicMock())

    assert response["statusCode"] == 200

    assert json.loads(response["body"]) == {
        "device_status": "Disconnected",
        "last_message_arrived": -2208988800000,
        "total_today": 0,
    }


def test_disconnect(basic_auth, secret_manager, events):
    request = http_request(path="/disconnect", method="POST")

    request["headers"]["Authorization"] = basic_auth

    response = handler(request, MagicMock())

    sqs_client = boto3.client("sqs")
    sqs_response = sqs_client.receive_message(QueueUrl=events)
    for message in sqs_response["Messages"]:
        assert json.loads(message["Body"])["detail-type"] == "logout"

    assert response["statusCode"] == 200
