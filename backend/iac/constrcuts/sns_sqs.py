from constructs import Construct

from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    aws_lambda_python_alpha as lambda_python,
    Duration,
    aws_lambda_event_sources as event_sources,
)


class SnsSqsConnection(Construct):
    """
    A construct that creates an SQS queue with a dead-letter queue,
    and subscribes the queue to an SNS topic and an AWS Lambda function.

    :param scope: The parent construct that this construct is part of.
    :param construct_id: The identifier of the construct.
    :param topic: The SNS topic that messages will be sent to.
    :param lambda_function: The Lambda function that will process the messages.
    :param queue_visibility: The visibility timeout of the SQS queue (default: 2 minutes).
    """

    @property
    def sqs_dlq(self) -> sqs.Queue:
        return self._dlq

    @property
    def sqs(self) -> sqs.Queue:
        return self._queue_listener

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sns_topic: sns.Topic,
        python_lambda: lambda_python.PythonFunction,
        queue_visibility: Duration = Duration.minutes(2),
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._dlq = sqs.Queue(
            self, f"{construct_id}-dlq", visibility_timeout=Duration.seconds(300)
        )

        self._queue_listener = sqs.Queue(
            self,
            f"{construct_id}-queue",
            visibility_timeout=queue_visibility,
            dead_letter_queue=sqs.DeadLetterQueue(queue=self._dlq, max_receive_count=5),
        )
        sns_topic.add_subscription(subscriptions.SqsSubscription(self._queue_listener))

        python_lambda.add_event_source(
            event_sources.SqsEventSource(
                self._queue_listener, report_batch_item_failures=True
            )
        )
