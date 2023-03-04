from constructs import Construct
from aws_cdk import (
    aws_secretsmanager as secretmanager,
    aws_ssm as ssm,
    SecretValue,
)


class Configuration(Construct):
    @property
    def admin_password_secret(self) -> secretmanager.Secret:
        return self._admin_password

    @property
    def google_credentials_secret(self) -> secretmanager.Secret:
        return self._google_credentials

    @property
    def openai_key_secret(self) -> secretmanager.Secret:
        return self._openai_key

    @property
    def sheet_url_parameter(self) -> ssm.StringParameter:
        return self._sheet_url

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._admin_password = secretmanager.Secret(
            self,
            "AdminPassword",
            generate_secret_string=secretmanager.SecretStringGenerator(
                exclude_characters=":"
            ),
        )
        self._google_credentials = secretmanager.Secret(
            self,
            "GoogleCredentials",
            secret_string_value=SecretValue.unsafe_plain_text("Replace"),
        )
        self._sheet_url = ssm.StringParameter(
            self, "GoogleSheetUrl", string_value="Replace"
        )
        self._openai_key = secretmanager.Secret(
            self,
            "OpenAiKey",
            secret_string_value=SecretValue.unsafe_plain_text("Replace"),
        )
