from unittest.mock import MagicMock
from ...src.chatgpt_integration.functions.summerize_chats.app import handler
from backend.src.utils.db_models.whatsapp_groups import WhatsAppGroup


def test_successful_chatgpt_summerize_creation(s3_raw_lake, group_db):
    handler({}, MagicMock())

    groups = WhatsAppGroup.scan()
    assert groups[0].group_id == "group-id"
