from ...src.admin_panel.functions.configuration.app import handler
from unittest.mock import MagicMock
import json
from aws_lambda_powertools.utilities import parameters
import os

from .utils import http_request
from ..conftest import SECRET_GOOGLE_AUTH, MOCK_SHEET_URL
from ...src.admin_panel.utils.dynamodb_models import ApplicationState, ClientStatus


def test_get_configuration(secret_manager, parameters_store, basic_auth):
    request = http_request(path="/configuration")
    request["headers"]["Authorization"] = basic_auth

    response = handler(request, MagicMock())

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "google_secret": SECRET_GOOGLE_AUTH,
        "sheet_url": MOCK_SHEET_URL,
    }


def test_post_configuration(secret_manager, parameters_store, basic_auth):
    request = http_request(
        path="/configuration",
        method="POST",
        body=json.dumps({"google_secret": "new auth", "sheet_url": "new url"}),
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


def test_get_device_status(basic_auth, application_state_db, secret_manager):
    request = http_request(path="/device-status", method="GET")

    request["headers"]["Authorization"] = basic_auth

    ApplicationState.update_client_status(ClientStatus.DISCONNECTED)

    response = handler(request, MagicMock())

    assert response["statusCode"] == 200

    assert json.loads(response["body"]) == {"device_status": "Disconnected"}
