from constructs import Construct
from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    Duration,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
)


class CollectWhatsAppGroups(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        whatsapp_group_table: dynamodb.Table,
        layer: lambda_python.PythonLayerVersion,
        chats_bucket: s3.Bucket,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        collect_lambda = lambda_python.PythonFunction(
            self,
            "CollectWhatsAppGroups",
            runtime=_lambda.Runtime.PYTHON_3_9,
            entry="backend",
            index="src/groups_collector/app.py",
            timeout=Duration.seconds(60),
            layers=[layer],
            environment={
                "WHATSAPP_GROUP_TABLE_NAME": whatsapp_group_table.table_name,
                "CHATS_BUCKET": chats_bucket.bucket_name,
            },
        )

        schedule_expression = events.Schedule.expression("rate(1 hour)")
        events.Rule(
            self,
            "MyScheduledRule",
            schedule=schedule_expression,
            targets=[targets.LambdaFunction(handler=collect_lambda)],
        )

        whatsapp_group_table.grant_write_data(collect_lambda)
        chats_bucket.grant_read(collect_lambda)
