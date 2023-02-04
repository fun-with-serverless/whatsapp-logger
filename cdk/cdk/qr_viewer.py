from .cdk_utils import prepare_layer

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_secretsmanager as secretmanager,
    CfnOutput,
)


class QRViewer(Stack):
    @property
    def lambda_url(self) -> str:
        return f"{self._url.url}qr-code"

    def __init__(
        self, scope: Construct, id: str, qr_bucket: s3.Bucket, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        secret = secretmanager.Secret(self, "QrLambdaPassword")

        qr_lambda = lambda_python.PythonFunction(
            self,
            "QrViewer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="../qr-viewer",
            index="src/app.py",
            environment={
                "QR_BUCKET_NAME": qr_bucket.bucket_name,
                "SECRETAUTH_PARAM_NAME": secret.secret_name,
                "QR_FILE_PATH": "qr.png",
            },
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self,
                    "PowerTools",
                    layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:18",
                ),
                prepare_layer(self, layer_name="QrViewerLocalReq", poetry_dir="../qr-viewer")
            ]
        )

        self._url = qr_lambda.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        qr_bucket.grant_read(qr_lambda)
        secret.grant_read(qr_lambda)

        CfnOutput(self, "GetQRUrl", value=self.lambda_url)
