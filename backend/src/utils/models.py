from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

from dacite import from_dict, Config


@dataclass(frozen=True)
class WhatsAppMessage:
    group_name: str
    group_id: str
    time: datetime
    message: str
    participant_id: str
    participant_handle: str
    participant_number: str
    has_media: bool
    participant_contact_name: Optional[str] = field(default="Unknown")

    @staticmethod
    def from_json(raw_message:str) -> "WhatsAppMessage":
        def converter(val):
            return datetime.fromtimestamp(val)

        message: WhatsAppMessage = from_dict(
            data_class=WhatsAppMessage,
            data=json.loads(raw_message),
            config=Config(type_hooks={datetime: converter}),
        )

        return message