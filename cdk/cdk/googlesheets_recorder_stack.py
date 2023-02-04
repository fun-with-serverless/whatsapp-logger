from .cdk_utils import prepare_layer
from constructs import Construct

from aws_cdk import (
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    CfnOutput,
    aws_secretsmanager as secretmanager,
    aws_ssm as ssm,
    Duration,
    aws_lambda_event_sources as event_sources,
)


class GoogleSheetsRecorder(Stack):
    @property
    def whatsapp_message_sns(self) -> sns.Topic:
        return self._whatsapp_messages

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dlq = sqs.Queue(
            self, "sheets-recorder-dlq", visibility_timeout=Duration.seconds(300)
        )

        sheets_recorder_queue = sqs.Queue(
            self,
            "sheets-recorder",
            visibility_timeout=Duration.minutes(2),
            dead_letter_queue=sqs.DeadLetterQueue(queue=dlq, max_receive_count=5),
        )
        whatsapp_messages = sns.Topic(self, "whatsapp-messages")
        whatsapp_messages.add_subscription(
            subscriptions.SqsSubscription(sheets_recorder_queue)
        )
        self._whatsapp_messages = whatsapp_messages

        google_credentials = secretmanager.Secret(self, "GoogleCredentials")
        sheet_url = ssm.StringParameter(
            self, "GoogleSheetUrl", string_value="Placeholder"
        )
        sheets_recorder = lambda_python.PythonFunction(
            self,
            "GoogleSheetRecorder",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="../googlesheets-recorder",
            index="src/app.py",
            timeout=Duration.minutes(1),
            environment={
                "GOOGLE_SECRET_AUTH_NAME": google_credentials.secret_name,
                "GOOGLE_SHEET_URL": sheet_url.parameter_name,
            },
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self,
                    "PowerTools",
                    layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:18",
                ),
                prepare_layer(
                    self,
                    layer_name="GoogleSheetRecorderLocalReq",
                    poetry_dir="../googlesheets-recorder",
                ),
            ],
        )

        google_credentials.grant_read(sheets_recorder)
        sheet_url.grant_read(sheets_recorder)

        sheets_recorder.add_event_source(
            event_sources.SqsEventSource(
                sheets_recorder_queue, report_batch_item_failures=True
            )
        )

        CfnOutput(self, "WhatsAppMessagesSns", value=whatsapp_messages.topic_arn)
