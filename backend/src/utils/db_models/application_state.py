from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    TTLAttribute,
    NumberAttribute,
    UTCDateTimeAttribute,
)
import os
from enum import Enum

DEFAULT_APPLICATION_STATE_DB_NAME = "APPLICATION_STATE_DB_REPLACE"
LAST_MESSAGE_ARRIVED_KEY = "last_message_arrived"


@dataclass(frozen=True)
class MessageStatistics:
    last_message_arrived: datetime
    total_today: int


class ClientStatus(Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"

    @classmethod
    def from_str(cls, value: str) -> "ClientStatus":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"{value} is not a valid member of {cls.__name__}")


class ApplicationState(Model):
    class Meta:
        table_name = os.environ.get(
            "APPLICATION_STATE_TABLE_NAME", DEFAULT_APPLICATION_STATE_DB_NAME
        )

    key = UnicodeAttribute(hash_key=True)
    value = UnicodeAttribute(null=True)
    value_number = NumberAttribute(null=True)
    value_date = UTCDateTimeAttribute(null=True)
    expires = TTLAttribute(null=True)

    @staticmethod
    def get_client_status() -> ClientStatus:
        return ClientStatus.from_str(ApplicationState.get("client_status").value)

    @staticmethod
    def update_client_status(status: ClientStatus) -> None:
        client_status = ApplicationState(key="client_status", value=status.value)
        client_status.save()

    @staticmethod
    def get_message_statistics() -> MessageStatistics:
        count_message_today = 0
        last_message_arrived = datetime.strptime(
            "1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        )
        try:
            when = datetime.now(tz=timezone.utc)
            count_message_today = int(
                ApplicationState.get(f"day_{when.timetuple().tm_yday}").value_number
            )
        except ApplicationState.DoesNotExist:
            pass

        try:
            last_message_arrived = ApplicationState.get(
                hash_key=LAST_MESSAGE_ARRIVED_KEY
            ).value_date
        except ApplicationState.DoesNotExist:
            pass

        return MessageStatistics(
            last_message_arrived=last_message_arrived, total_today=count_message_today
        )

    @staticmethod
    def update_new_message_arrived(when: datetime) -> None:
        try:
            val = ApplicationState.get(hash_key=f"day_{when.timetuple().tm_yday}")
        except ApplicationState.DoesNotExist:
            val = ApplicationState(
                key=f"day_{when.timetuple().tm_yday}", value_number=0
            )
            val.save()

        val.update(
            actions=[
                ApplicationState.value_number.set(ApplicationState.value_number + 1),
                ApplicationState.expires.set(
                    datetime.now(tz=timezone.utc) + timedelta(days=1)
                ),
            ]
        )

        try:
            val = ApplicationState.get(hash_key=LAST_MESSAGE_ARRIVED_KEY)
        except ApplicationState.DoesNotExist:
            val = ApplicationState(
                key=LAST_MESSAGE_ARRIVED_KEY,
                value_date=datetime.now(tz=timezone.utc),
            )
            val.save()

        val.update(
            actions=[
                ApplicationState.value_date.set(datetime.now(tz=timezone.utc)),
            ]
        )
