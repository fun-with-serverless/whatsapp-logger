from dataclasses import dataclass


@dataclass(frozen=True)
class ChatGPTSummary:
    content: str
    group_name: str
    group_id: str
