from constructs import Construct

from aws_cdk import (
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    CfnOutput,
)
from constructs import Construct


class GoogleSheetsRecorder(Stack):
    @property
    def whatsapp_message_sns(self) -> sns.Topic:
        return self._whatsapp_messages

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        sheets_recorder_queue = sqs.Queue(self, "sheets-recorder", fifo=True)
        whatsapp_messages = sns.Topic(self, "whatsapp-messages", fifo=True)
        whatsapp_messages.add_subscription(
            subscriptions.SqsSubscription(sheets_recorder_queue)
        )
        self._whatsapp_messages = whatsapp_messages

        CfnOutput(self, "WhatsAppMessagesSns", value=whatsapp_messages.topic_arn)
