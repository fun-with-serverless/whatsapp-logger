from .cdk_utils import prepare_layer
from .configuration import Configuration
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    aws_s3 as s3,
    Duration,
    aws_events as eb,
)


class AdminPanel(Stack):
    @property
    def lambda_url(self) -> str:
        return f"{self._url.url}"

    def __init__(
        self,
        scope: Construct,
        id: str,
        qr_bucket: s3.Bucket,
        configuration: Configuration,
        event_bus: eb.EventBus,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        qr_lambda = lambda_python.PythonFunction(
            self,
            "QrViewer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="../admin-panel",
            index="src/functions/configuration/app.py",
            timeout=Duration.seconds(30),
            environment={
                "QR_BUCKET_NAME": qr_bucket.bucket_name,
                "SECRETAUTH_PARAM_NAME": configuration.admin_password_secret.secret_name,
                "QR_FILE_PATH": "qr.png",
                "GOOGLE_SECRET_AUTH_NAME": configuration.google_credentials_secret.secret_name,
                "GOOGLE_SHEET_URL": configuration.sheet_url_parameter.parameter_name,
            },
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self,
                    "PowerTools",
                    layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:18",
                ),
                prepare_layer(
                    self, layer_name="QrViewerLocalReq", poetry_dir="../admin-panel"
                ),
            ],
        )

        self._url = qr_lambda.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        qr_bucket.grant_read(qr_lambda)
        configuration.admin_password_secret.grant_read(qr_lambda)
        configuration.admin_password_secret.grant_write(qr_lambda)
        configuration.google_credentials_secret.grant_read(qr_lambda)
        configuration.google_credentials_secret.grant_write(qr_lambda)
        configuration.sheet_url_parameter.grant_read(qr_lambda)
        configuration.sheet_url_parameter.grant_write(qr_lambda)
        event_bus.grant_put_events_to(qr_lambda)
