from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    BooleanAttribute,
    UTCDateTimeAttribute,
)
import os

DEFAULT_APPLICATION_STATE_DB_NAME = "WHATSAPP_GROUP__DB_REPLACE"


class WhatsAppGroup(Model):
    class Meta:
        table_name = os.environ.get(
            "WHATSAPP_GROUP_TABLE_NAME", DEFAULT_APPLICATION_STATE_DB_NAME
        )

    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    requires_daily_summary = BooleanAttribute(default=False)
    always_mark_read = BooleanAttribute(default=False)
    created = UTCDateTimeAttribute(default=datetime.now)
