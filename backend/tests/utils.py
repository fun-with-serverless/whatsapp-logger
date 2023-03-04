import json
from typing import List


def get_sqs_body(group_name: str, epoch_time: int = 1612081880) -> str:
    return json.dumps(
        {
            "Message": '{{"group_name": "{group_name}", "group_id": "test_id", "time": {epoch_time}, "message": "test_message", "participant_id": "test_participant_id", "participant_handle": "test_handle", "participant_number": "test_number", "participant_contact_name": "test_name", "has_media": false}}'.format(
                group_name=group_name, epoch_time=epoch_time
            )
        }
    )


class MockOpenAi:
    api_key: str

    class ChatCompletion:
        @classmethod
        def create(cls, model: str, messages: List[dict]):
            return {"choices": [{"message": {"content": "haaa"}}]}
