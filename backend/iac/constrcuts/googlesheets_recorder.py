from constructs import Construct

from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    Duration,
    aws_lambda_event_sources as event_sources,
    aws_ssm as ssm,
    aws_secretsmanager as secretmanager,
)


class GoogleSheetsRecorder(Construct):
    @property
    def whatsapp_message_sns(self) -> sns.Topic:
        return self._whatsapp_messages

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        google_credentials_secret: secretmanager.Secret,
        sheet_url_parameter: ssm.StringParameter,
        layer: lambda_python.PythonLayerVersion,
        **kwargs,
    ) -> None:
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

        sheets_recorder = lambda_python.PythonFunction(
            self,
            "GoogleSheetRecorder",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend/src/googlesheets_recorder",
            index="app.py",
            timeout=Duration.minutes(1),
            environment={
                "GOOGLE_SECRET_AUTH_NAME": google_credentials_secret.secret_name,
                "GOOGLE_SHEET_URL": sheet_url_parameter.parameter_name,
            },
            layers=[layer],
        )

        google_credentials_secret.grant_read(sheets_recorder)
        sheet_url_parameter.grant_read(sheets_recorder)

        sheets_recorder.add_event_source(
            event_sources.SqsEventSource(
                sheets_recorder_queue, report_batch_item_failures=True
            )
        )
