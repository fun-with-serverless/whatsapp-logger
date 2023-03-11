from enum import Enum
import functools
import json
import os

import boto3


class DetailType(Enum):
    LOGOUT = "logout"
    SUMMARY = "summary"


class Source(Enum):
    ADMIN = "admin"
    CHATGPT = "chatgpt"


class Client:
    def send_message(
        self, detail_type: DetailType, source: Source, detail: dict
    ) -> None:
        events = Client._get_events()
        events.put_events(
            Entries=[
                {
                    "EventBusName": os.environ["EVENT_BUS_ARN"],
                    "Detail": json.dumps(detail),
                    "DetailType": detail_type.value,
                    "Source": source.value,
                }
            ]
        )

    @staticmethod
    @functools.cache
    def _get_events():
        return boto3.client("events")
