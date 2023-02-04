from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import (
    LambdaFunctionUrlResolver,
    Response,
    content_types,
)
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.event_handler.exceptions import (
    UnauthorizedError,
)
import base64
from http import HTTPStatus
import boto3
import os

s3 = boto3.client("s3")

USER = "admin"
AUTH_HTML_TEMPLATE = """
            <!DOCTYPE html>
<html>
<head>
  <title>Basic Authentication</title>
  <style>
    /* Add some general styles for the form */
    form {
      width: 300px;
      margin: 0 auto;
      padding: 10px;
      border: 1px solid gray;
      border-radius: 5px;
    }

    /* Add some styles for the form labels */
    label {
      font-size: 14px;
      font-weight: bold;
      margin-bottom: 5px;
    }

    /* Add some styles for the form inputs */
    input[type="text"], input[type="password"] {
      width: 100%;
      padding: 12px 20px;
      margin: 8px 0;
      box-sizing: border-box;
      border: 1px solid gray;
      border-radius: 4px;
    }

    /* Add some styles for the submit button */
    input[type="button"] {
      width: 100%;
      background-color: #4CAF50;
      color: white;
      padding: 14px 20px;
      margin: 8px 0;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    /* Add some styles for the image container*/
    #image-container {
        padding: 10px;
        text-align: center;
    }
    /* Add some styles for the image*/
    #image-container img{
        width:33%;
    }
  </style>
</head>
<body>

<form>
  <label for="username">Username:</label>
  <input type="text" id="username" name="username"><br><br>
  <label for="password">Password:</label>
  <input type="password" id="password" name="password"><br><br>
  <input type="button" value="Submit" onclick="submitForm()">
</form>

<div id="image-container"></div>

<script>
  function submitForm() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", window.location.href, true);
    xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
    xhr.responseType = "blob";
    xhr.onload = function () {
        if (xhr.status === 200) {
            var blob = xhr.response;
            var img = document.createElement("img");
            img.src = URL.createObjectURL(blob);
            document.getElementById("image-container").appendChild(img);
        } else {
            alert("Authentication failed. Please check your username and password.");
        }
    }
    xhr.send();
  }
</script>

</body>
</html>

"""

logger = Logger()
app = LambdaFunctionUrlResolver()


@app.get("/qr-code")
def get_qr_code():
    encoded_auth = app.current_event.get_header_value(name="authorization")
    logger.info(app.current_event.headers)
    if encoded_auth and encoded_auth.startswith("Basic"):
        logger.info("Basic auth arrived", auth_details=encoded_auth)
        # Decode the value
        decoded_auth = base64.b64decode(encoded_auth[6:]).decode()

        # Split the decoded value into a username and password
        username, password = decoded_auth.split(":")

        # Check if the username and password match the expected values
        if username == "admin" and password == parameters.get_secret(
            os.environ["SECRETAUTH_PARAM_NAME"]
        ):
            logger.info("USer logged in")
            return Response(
                status_code=200, content_type="image/png", body=get_qr_image()
            )
        else:
            logger.info("Invalid user/pass", user=username)
            raise UnauthorizedError("Unauthorized")
    else:
        logger.info("Missing basic auth")
        return Response(
            status_code=HTTPStatus.OK,
            content_type=content_types.TEXT_HTML,
            body=AUTH_HTML_TEMPLATE,
        )


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)


def get_qr_image() -> bytes:
    bucket_name = os.environ["QR_BUCKET_NAME"]
    file_path = os.environ["QR_FILE_PATH"]
    return s3.get_object(Bucket=bucket_name, Key=file_path)["Body"].read()
