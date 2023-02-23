from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
import os
from enum import Enum

DEFAULT_APPLICATION_STATE_DB_NAME = "APPLICATION_STATE_DB_REPLACE"


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
    value = UnicodeAttribute()
    ttl = 

    @staticmethod
    def get_client_status() -> ClientStatus:
        return ClientStatus.from_str(ApplicationState.get("client_status").value)

    @staticmethod
    def update_client_status(status: ClientStatus) -> None:
        client_status = ApplicationState(key="client_status", value=status.value)
        client_status.save()

    @staticmethod
    def update_new_message_arrived(when: datetime) -> None:
        try:
            val = ApplicationState.get(hash_key=f"day_{datetime.datetime.now().timetuple().tm_yday}")
        except ApplicationState.DoesNotExist:
            val = ApplicationState(f"day_{datetime.datetime.now().timetuple().tm_yday}", 0)
            val.save()
        
        val.update(actions=[ApplicationState.value.set(ApplicationState.value+1)])
        
