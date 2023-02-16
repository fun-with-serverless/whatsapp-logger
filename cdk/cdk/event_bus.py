from aws_cdk import (
    Stack,
    aws_events as eb,
)
from constructs import Construct


class EventBus(Stack):
    @property
    def eventbus(self) -> eb.EventBus:
        return self.event_bus

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.event_bus = eb.EventBus(self, "WhatsAppSystemBus")
