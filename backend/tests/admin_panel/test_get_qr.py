from ...src.admin_panel.functions.configuration.app import handler
from unittest.mock import MagicMock
import base64
from .utils import http_request


def test_handler_not_authenticated_return_login():

    response = handler(http_request(), MagicMock())
    print(response)

    assert response["statusCode"] == 401


def test_handler_invalid_authenticated_return_401(monkeypatch):
    request = http_request()
    request["headers"]["Authorization"] = "Basic YWRtaW46cGFzc3dvcmQ="
    monkeypatch.setenv("LOGIN_USER", "not-admin")

    response = handler(request, MagicMock())

    assert response["statusCode"] == 401


def test_handler_valid_authenticated_return_200_with_a_file(
    s3, secret_manager, basic_auth
):
    request = http_request()
    request["headers"]["Authorization"] = basic_auth

    response = handler(request, MagicMock())

    assert response["statusCode"] == 200
    assert base64.b64decode(response["body"]).decode("utf-8") == "test"
