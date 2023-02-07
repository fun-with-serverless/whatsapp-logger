from constructs import Construct
from aws_cdk import (
    Stack,
    aws_secretsmanager as secretmanager,
    CfnOutput,
    aws_ssm as ssm,
    SecretValue,
)


class Configuration(Stack):
    @property
    def admin_password_secret(self) -> secretmanager.Secret:
        return self.admin_password

    @property
    def google_credentials_secret(self) -> secretmanager.Secret:
        return self.google_credentials

    @property
    def sheet_url_parameter(self) -> ssm.StringParameter:
        return self.sheet_url

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.admin_password = secretmanager.Secret(self, "AdminPassword")
        self.google_credentials = secretmanager.Secret(
            self,
            "GoogleCredentials",
            secret_string_value=SecretValue.unsafe_plain_text("Replace"),
        )
        self.sheet_url = ssm.StringParameter(
            self, "GoogleSheetUrl", string_value="Replace"
        )

        CfnOutput(
            self,
            "AdminPasswordURL",
            value=f"https://{self.region}.console.aws.amazon.com/secretsmanager/secret?name={self.admin_password.secret_name}",
        )
