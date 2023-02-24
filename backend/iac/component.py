from .constrcuts.state import State
from .constrcuts.configuration import Configuration
from .constrcuts.admin_panel import AdminPanel
from .constrcuts.googlesheets_recorder import GoogleSheetsRecorder
from .constrcuts.dashboard import Dashboard
from .constrcuts.message_statistics import MessageStatistics
from .utils.cdk_utils import prepare_layer

from constructs import Construct

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_events as eb,
    aws_sns as sns,
    aws_s3 as s3,
)


class Backend(Stack):
    @property
    def event_bus(self) -> eb.EventBus:
        return self._event_bus

    @property
    def whatsapp_message_sns(self) -> sns.Topic:
        return self._whatsapp_message_sns

    @property
    def qr_bucket(self) -> s3.Bucket:
        return self._state.qr_bucket

    @property
    def website_domain(self) -> str:
        return self._dashboard.dashboard_domain

    @property
    def website_s3_bucket(self) -> s3.IBucket:
        return self._dashboard.website_bucket

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._whatsapp_message_sns = sns.Topic(self, "whatsapp-messages")
        self._event_bus = eb.EventBus(self, "WhatsAppSystemBus")
        self._state = State(self, "State")
        configuration = Configuration(self, "Configuration")
        layer = prepare_layer(
            self, layer_name="BackendLocalReq", poetry_dir="backend/admin-panel"
        )
        admin = AdminPanel(
            self,
            "AdminPanel",
            self._state.qr_bucket,
            configuration.admin_password_secret,
            configuration.google_credentials_secret,
            configuration.sheet_url_parameter,
            self._event_bus,
            self._state.state_table,
            layer,
        )
        self._recorder = GoogleSheetsRecorder(
            self,
            "GoogleSheetsRecorder",
            configuration.google_credentials_secret,
            configuration.sheet_url_parameter,
            layer,
            whatsapp_messages=self._whatsapp_message_sns,
        )

        self._dashboard = Dashboard(self, "Dashboard")

        MessageStatistics(
            self,
            "MessageStatistics",
            application_state_table=self._state.state_table,
            layer=layer,
            whatsapp_messages=self._whatsapp_message_sns,
        )

        CfnOutput(
            self,
            "AdminPasswordURL",
            value=f"https://{self.region}.console.aws.amazon.com/secretsmanager/secret?name={configuration.admin_password_secret.secret_name}",
        )

        CfnOutput(
            self,
            "DashboardURL",
            value=f"https://{self._dashboard.dashboard_domain}",
        )

        CfnOutput(
            self,
            "BackendURL",
            export_name="BackendURL",
            value=admin.lambda_url,
        )
