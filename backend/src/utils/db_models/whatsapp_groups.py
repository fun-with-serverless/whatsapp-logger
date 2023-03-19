from datetime import datetime
from enum import Enum
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    BooleanAttribute,
    UTCDateTimeAttribute,
)
import os

from ...utils.general import EnumAttribute, enum_from_str

DEFAULT_APPLICATION_STATE_DB_NAME = "WHATSAPP_GROUP__DB_REPLACE"


class SummaryStatus(Enum):
    NONE = "None"
    MYSELF = "Myself"
    ORIGINAL_GROUP = "Original_Group"
    OTHER = "Other"

    @classmethod
    def from_str(cls, value: str) -> "SummaryStatus":
        return enum_from_str(SummaryStatus, value)


class SummaryLanguage(Enum):
    ENGLISH = "English"
    HEBREW = "Hebrew"
    MANDARIN_CHINESE = "Mandarin_Chinese"
    SPANISH = "Spanish"
    HINDI = "Hindi"
    ARABIC = "Arabic"
    FRENCH = "French"
    GERMAN = "German"

    @classmethod
    def from_str(cls, value: str) -> "SummaryLanguage":
        return enum_from_str(SummaryLanguage, value)


class WhatsAppGroup(Model):
    class Meta:
        table_name = os.environ.get(
            "WHATSAPP_GROUP_TABLE_NAME", DEFAULT_APPLICATION_STATE_DB_NAME
        )

    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    requires_daily_summary = EnumAttribute(
        enum_cls=SummaryStatus, default=SummaryStatus.NONE
    )
    always_mark_read = BooleanAttribute(default=False)
    created = UTCDateTimeAttribute(default=datetime.now)
    send_summary_to_group_id = UnicodeAttribute(null=True)
    summary_language = EnumAttribute(
        enum_cls=SummaryLanguage, default=SummaryLanguage.ENGLISH
    )
