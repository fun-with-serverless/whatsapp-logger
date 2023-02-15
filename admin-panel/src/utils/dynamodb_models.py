from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
import os
from enum import Enum


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
        table_name = os.environ.get("APPLICATION_STATE_TABLE_NAME", "Replace")

    key = UnicodeAttribute(hash_key=True)
    value = UnicodeAttribute()

    @staticmethod
    def get_client_status() -> ClientStatus:
        return ClientStatus.from_str(ApplicationState.get("client_status").value)

    @staticmethod
    def update_client_status(status: ClientStatus) -> None:
        client_status = ApplicationState(key="client_status", value=status.value)
        client_status.save()
        
