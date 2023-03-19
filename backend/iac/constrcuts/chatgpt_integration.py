from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    Duration,
    aws_s3 as s3,
    aws_sns as sns,
    aws_kinesisfirehose_alpha as fh,
    aws_kinesisfirehose_destinations_alpha as destinations,
    aws_secretsmanager as secretmanager,
    aws_events as events,
    aws_events_targets as targets,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_logs as logs,
    aws_dynamodb as dynamodb,
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
        chatgpt_key: secretmanager.Secret,
        event_bus: events.EventBus,
        groups_db: dynamodb.Table,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        s3_destination = destinations.S3Bucket(
            bucket=chats_bucket,
            buffering_interval=Duration.seconds(900),
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

        summerize_chats = lambda_python.PythonFunction(
            self,
            "SummerizeChats",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/chatgpt_integration/functions/summerize_chats/app.py",
            timeout=Duration.seconds(120),
            layers=[layer],
            environment={
                "CHATS_BUCKET": chats_bucket.bucket_name,
                "WHATSAPP_GROUP_TABLE_NAME": groups_db.table_name,
            },
        )

        chatgpt_call = lambda_python.PythonFunction(
            self,
            "ChatGPTCall",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/chatgpt_integration/functions/chatgpt_call/app.py",
            timeout=Duration.seconds(60),
            layers=[layer],
            environment={
                "OPENAI_KEY": chatgpt_key.secret_name,
                "CHATS_BUCKET": chats_bucket.bucket_name,
                "WHATSAPP_GROUP_TABLE_NAME": groups_db.table_name,
            },
        )

        delete_buckup = lambda_python.PythonFunction(
            self,
            "DeleteOldChats",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/chatgpt_integration/functions/delete_old_summary/app.py",
            timeout=Duration.seconds(60),
            layers=[layer],
            environment={
                "CHATS_BUCKET": chats_bucket.bucket_name,
            },
        )

        send_to_client = lambda_python.PythonFunction(
            self,
            "SendSummaryToClient",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/chatgpt_integration/functions/send_summary_to_client/app.py",
            timeout=Duration.seconds(30),
            layers=[layer],
            environment={
                "EVENT_BUS_ARN": event_bus.event_bus_arn,
                "WHATSAPP_GROUP_TABLE_NAME": groups_db.table_name,
            },
        )

        state_machine = self._build_stf(
            summerize_chats, chatgpt_call, delete_buckup, send_to_client
        )

        schedule_expression = events.Schedule.expression(
            "cron(0 1 * * ? *)"
        )  # Runs at 1:00:00 AM UTC every day
        events.Rule(
            self,
            "MyScheduledRule",
            schedule=schedule_expression,
            targets=[
                targets.SfnStateMachine(
                    machine=state_machine,
                    input=events.RuleTargetInput.from_object(
                        {"bucket": chats_bucket.bucket_name}
                    ),
                )
            ],
        )

        ds.grant_put_records(write_chats_to_s3)
        chatgpt_key.grant_read(chatgpt_call)
        chats_bucket.grant_put(summerize_chats)
        chats_bucket.grant_put(delete_buckup)
        chats_bucket.grant_delete(delete_buckup)
        chats_bucket.grant_read(delete_buckup)
        chats_bucket.grant_read(summerize_chats)
        chats_bucket.grant_read(chatgpt_call)
        event_bus.grant_put_events_to(send_to_client)
        groups_db.grant_read_data(send_to_client)
        groups_db.grant_read_data(chatgpt_call)
        groups_db.grant_read_data(summerize_chats)

        SnsSqsConnection(self, "WriteToS3", whatsapp_messages, write_chats_to_s3)

    def _build_stf(
        self,
        summerize_chats: lambda_python.PythonFunction,
        chatgpt_call: lambda_python.PythonFunction,
        delete_buckup: lambda_python.PythonFunction,
        send_to_client: lambda_python.PythonFunction,
    ) -> sfn.StateMachine:
        summerize_step = sfn_tasks.LambdaInvoke(
            self,
            "Summerize Chats",
            lambda_function=summerize_chats,
        )

        send_to_chatgpt = sfn_tasks.LambdaInvoke(
            self,
            "Send to ChatGPT",
            lambda_function=chatgpt_call,
            output_path="$.Payload",
        )

        send_to_chatgpt.add_retry(errors=["Lambda.Unknown"])

        delete_and_backup_step = sfn_tasks.LambdaInvoke(
            self,
            "Backup chats and delete old ones",
            lambda_function=delete_buckup,
        )

        send_to_client_step = sfn_tasks.LambdaInvoke(
            self,
            "Send summary to client",
            lambda_function=send_to_client,
        )

        map = sfn.Map(
            self, "Map State", max_concurrency=2, input_path="$.Payload.s3_files"
        )

        success = sfn.Succeed(self, "All summery messages were sent")

        map.iterator(send_to_chatgpt.next(send_to_client_step))

        definition = summerize_step.next(map).next(delete_and_backup_step).next(success)
        return sfn.StateMachine(
            self,
            "SendToChatGPT",
            definition=definition,
            timeout=Duration.minutes(5),
            logs=sfn.LogOptions(
                destination=logs.LogGroup(self, "MyLogGroup"), level=sfn.LogLevel.ALL
            ),
        )
