from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    Duration,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
)

from .sns_sqs import SnsSqsConnection


class MessageStatistics(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        application_state_table: dynamodb.Table,
        layer: lambda_python.PythonLayerVersion,
        whatsapp_messages: sns.Topic,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        message_statistics = lambda_python.PythonFunction(
            self,
            "MessageStatistics",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/admin_panel/functions/messages_statistics/app.py",
            timeout=Duration.seconds(30),
            layers=[layer],
            environment={
                "APPLICATION_STATE_TABLE_NAME": application_state_table.table_name,
            },
        )

        application_state_table.grant_write_data(message_statistics)
        application_state_table.grant_read_data(message_statistics)

        SnsSqsConnection(
            self, "StatisticsRecorder", whatsapp_messages, message_statistics
        )
