from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    Duration,
    aws_s3 as s3,
    aws_sns as sns,
    aws_kinesisfirehose_alpha as fh,
    aws_kinesisfirehose_destinations_alpha as destinations,
)

from .sns_sqs import SnsSqsConnection


class ChatGPTIntegration(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        chats_bucket: s3.Bucket,
        layer: lambda_python.PythonLayerVersion,
        whatsapp_messages: sns.Topic,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        s3_destination = destinations.S3Bucket(
            bucket=chats_bucket,
            buffering_interval=Duration.seconds(60),
            data_output_prefix="!{timestamp:yyyy}.!{timestamp:MM}.!{timestamp:dd}/",
            error_output_prefix="myFirehoseFailures/!{firehose:error-output-type}/Year=!{timestamp:yyyy}/Month=!{timestamp:MM}/Day=!{timestamp:dd}",
        )

        ds = fh.DeliveryStream(self, "Delivery Stream", destinations=[s3_destination])

        write_chats_to_s3 = lambda_python.PythonFunction(
            self,
            "ChatGPTIntegration",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/chatgpt_integration/functions/write_chats_to_s3/app.py",
            timeout=Duration.seconds(30),
            layers=[layer],
            environment={
                "CHATS_FIREHOSE": ds.delivery_stream_name,
            },
        )

        ds.grant_put_records(write_chats_to_s3)

        SnsSqsConnection(self, "WriteToS3", whatsapp_messages, write_chats_to_s3)
