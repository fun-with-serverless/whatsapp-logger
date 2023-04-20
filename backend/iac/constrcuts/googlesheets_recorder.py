from constructs import Construct
from .sns_sqs import SnsSqsConnection
from aws_cdk import (
    aws_sns as sns,
    aws_lambda_python_alpha as lambda_python,
    Duration,
    aws_ssm as ssm,
    aws_secretsmanager as secretmanager,
)
from .predefined_lambda import PythonLambda


class GoogleSheetsRecorder(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        google_credentials_secret: secretmanager.Secret,
        sheet_url_parameter: ssm.StringParameter,
        layer: lambda_python.PythonLayerVersion,
        whatsapp_messages: sns.Topic,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        sheets_recorder = PythonLambda(
            self,
            "GoogleSheetRecorder",
            entry="backend",
            index="src/googlesheets_recorder/app.py",
            timeout=Duration.minutes(1),
            environment={
                "GOOGLE_SECRET_AUTH_NAME": google_credentials_secret.secret_name,
                "GOOGLE_SHEET_URL": sheet_url_parameter.parameter_name,
            },
            layers=[layer],
        )

        SnsSqsConnection(self, "SheetsRecorder", whatsapp_messages, sheets_recorder)

        google_credentials_secret.grant_read(sheets_recorder)
        sheet_url_parameter.grant_read(sheets_recorder)
