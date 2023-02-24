from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import (
    LambdaFunctionUrlResolver,
)
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.event_handler.exceptions import (
    UnauthorizedError,
)
import base64
import os

logger = Logger()
USER = "admin"


def basic_authenticate(app: LambdaFunctionUrlResolver):
    def inner(function):
        def wrapper(*args, **kwargs):
            encoded_auth = app.current_event.get_header_value(name="authorization")
            logger.info(app.current_event.headers)
            if encoded_auth and encoded_auth.startswith("Basic"):
                logger.info("Basic auth arrived", auth_details=encoded_auth)
                # Decode the value
                decoded_auth = base64.b64decode(encoded_auth[6:]).decode()

                # Split the decoded value into a username and password
                username, password = decoded_auth.split(":")

                # Check if the username and password match the expected values
                if username == os.environ.get(
                    "LOGIN_USER", USER
                ) and password == parameters.get_secret(
                    os.environ["SECRETAUTH_PARAM_NAME"]
                ):
                    logger.info("User logged in")
                    return function(*args, **kwargs)
                else:
                    logger.info("Invalid user/pass", user=username)
                    raise UnauthorizedError("Unauthorized")
            else:
                logger.info("Missing basic auth")
                raise UnauthorizedError("Unauthorized")

        return wrapper

    return inner
