from aws_cdk import (
    Stack,
    aws_events as eb,
    aws_sqs as sqs,
    aws_events_targets as events_targets,
)
from constructs import Construct


class EventBus(Stack):
    @property
    def eventbus(self) -> eb.EventBus:
        return self.event_bus

    @property
    def sqs_target(self) -> sqs.Queue:
        return self.queue

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.event_bus = eb.EventBus(self, "EventBus")

        self.queue = sqs.Queue(self, "UpdteWhatsAppListener")

        eb.Rule(
            self,
            "LogoutEventRule",
            event_bus=self.event_bus,
            event_pattern={"detail_type": ["WhatsApp Logout"], "source": ["admin"]},
            targets=[events_targets.SqsQueue(self.queue)],
        )
