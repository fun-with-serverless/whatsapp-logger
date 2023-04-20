from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    aws_s3 as s3,
    Duration,
    aws_events as eb,
    aws_events_targets as events_targets,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_ssm as ssm,
    aws_secretsmanager as secretmanager,
)

from .predefined_lambda import PythonLambda


class AdminPanel(Construct):
    @property
    def lambda_url(self) -> str:
        return f"{self._url.url}"

    def __init__(
        self,
        scope: Construct,
        id: str,
        qr_bucket: s3.Bucket,
        admin_password_secret: secretmanager.Secret,
        google_credentials_secret: secretmanager.Secret,
        sheet_url_parameter: ssm.StringParameter,
        event_bus: eb.EventBus,
        application_state_table: dynamodb.Table,
        layer: lambda_python.PythonLayerVersion,
        openai_key: secretmanager.Secret,
        whatsapp_group_table: dynamodb.Table,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        qr_lambda = PythonLambda(
            self,
            "Admin",
            entry="backend",
            index="src/admin_panel/functions/configuration/app.py",
            timeout=Duration.seconds(30),
            environment={
                "QR_BUCKET_NAME": qr_bucket.bucket_name,
                "SECRETAUTH_PARAM_NAME": admin_password_secret.secret_name,
                "QR_FILE_PATH": "qr.png",
                "GOOGLE_SECRET_AUTH_NAME": google_credentials_secret.secret_name,
                "OPENAI_KEY": openai_key.secret_name,
                "GOOGLE_SHEET_URL": sheet_url_parameter.parameter_name,
                "EVENT_BUS_ARN": event_bus.event_bus_arn,
                "APPLICATION_STATE_TABLE_NAME": application_state_table.table_name,
                "WHATSAPP_GROUP_TABLE_NAME": whatsapp_group_table.table_name,
            },
            layers=[layer],
        )

        status_dlq = sqs.Queue(self, "StatusDLQ")

        agent_status = PythonLambda(
            self,
            "UpdateStatus",
            entry="backend",
            index="src/admin_panel/functions/agent_status/app.py",
            timeout=Duration.seconds(30),
            dead_letter_queue=status_dlq,
            environment={
                "APPLICATION_STATE_TABLE_NAME": application_state_table.table_name,
            },
            layers=[layer],
        )

        self._url = qr_lambda.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        qr_bucket.grant_read(qr_lambda)
        admin_password_secret.grant_read(qr_lambda)
        admin_password_secret.grant_write(qr_lambda)
        openai_key.grant_read(qr_lambda)
        openai_key.grant_write(qr_lambda)
        google_credentials_secret.grant_read(qr_lambda)
        google_credentials_secret.grant_write(qr_lambda)
        sheet_url_parameter.grant_read(qr_lambda)
        sheet_url_parameter.grant_write(qr_lambda)
        event_bus.grant_put_events_to(qr_lambda)
        application_state_table.grant_write_data(agent_status)
        application_state_table.grant_read_data(qr_lambda)
        whatsapp_group_table.grant_read_data(qr_lambda)
        whatsapp_group_table.grant_write_data(qr_lambda)

        eb.Rule(
            self,
            "WhatsAppClientStatusEvent",
            event_bus=event_bus,
            event_pattern={
                "detail_type": ["status-change"],
                "source": ["whatsapp-client"],
            },
            targets=[events_targets.LambdaFunction(agent_status)],
        )
