from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import event_source, EventBridgeEvent
from dacite import from_dict

from ....utils.dynamodb_models import ApplicationState, ClientStatus
from dataclasses import dataclass


logger = Logger()


@dataclass(frozen=True)
class EventData:
    status: str


@event_source(data_class=EventBridgeEvent)
@logger.inject_lambda_context(log_event=True)
def handler(event: EventBridgeEvent, context: LambdaContext):
    current_status = from_dict(data_class=EventData, data=event.detail)
    ApplicationState.update_client_status(ClientStatus.from_str(current_status.status))
