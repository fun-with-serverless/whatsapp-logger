from src.app import handler
from unittest.mock import MagicMock
import pytest
import moto
import boto3
import base64


@pytest.fixture
def http_request():
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/qr-code",
        "rawQueryString": "",
        "headers": {},
        "requestContext": {
            "accountId": "anonymous",
            "apiId": "e6sirlw4f6kx7s6osdrik5qs4i0veiia",
            "domainName": "e6sirlw4f6kx7s6osdrik5qs4i0veiia.lambda-url.us-east-1.on.aws",
            "domainPrefix": "e6sirlw4f6kx7s6osdrik5qs4i0veiia",
            "http": {
                "method": "GET",
                "path": "/qr-code",
                "protocol": "HTTP/1.1",
                "sourceIp": "87.71.254.204",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70",
            },
            "requestId": "fc5d0537-0fc1-444a-ab3e-90b3c163bb97",
            "routeKey": "$default",
            "stage": "$default",
            "time": "04/Feb/2023:20:44:27 +0000",
            "timeEpoch": 1675543467633,
        },
        "isBase64Encoded": False,
    }


def test_handler_not_authenticated_return_login(http_request):

    response = handler(http_request, MagicMock())
    print(response)

    assert response["statusCode"] == 200
    assert "Basic Authentication" in response["body"]


def test_handler_invalid_authenticated_return_401(http_request, monkeypatch):

    http_request["headers"]["Authorization"] = "Basic YWRtaW46cGFzc3dvcmQ="
    monkeypatch.setenv("LOGIN_USER", "not-admin")

    response = handler(http_request, MagicMock())

    assert response["statusCode"] == 401


@moto.mock_secretsmanager
@moto.mock_s3
def test_handler_valid_authenticated_return_200_with_a_file(http_request, monkeypatch):

    client = boto3.client("secretsmanager")

    # Create a secret in Secrets Manager
    secret_name = "secret"
    secret_string = "password"
    user = "admin"
    client.create_secret(Name=secret_name, SecretString=secret_string)

    conn = boto3.client("s3")
    conn.create_bucket(Bucket="bucket")
    conn.put_object(Bucket="bucket", Key="qr.jpg", Body="test")
    basic_auth = base64.b64encode(f"{user}:{secret_string}".encode()).decode()
    http_request["headers"]["Authorization"] = f"Basic {basic_auth}"

    monkeypatch.setenv("LOGIN_USER", "admin")
    monkeypatch.setenv("SECRETAUTH_PARAM_NAME", secret_name)
    monkeypatch.setenv("QR_BUCKET_NAME", "bucket")
    monkeypatch.setenv("QR_FILE_PATH", "qr.jpg")

    response = handler(http_request, MagicMock())

    assert response["statusCode"] == 200
    assert base64.b64decode(response["body"]).decode("utf-8") == "test"
