from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from ...src.groups_collector.app import handler
from backend.src.utils.db_models.whatsapp_groups import SummaryStatus, WhatsAppGroup


@pytest.mark.data_date(datetime.now(tz=timezone.utc))
def test_successful_chatgpt_summerize_creation(s3_raw_lake, group_db):
    handler({}, MagicMock())

    groups = WhatsAppGroup.scan()
    assert list(groups)[0].id == "group-id"


@pytest.mark.data_date(datetime.now(tz=timezone.utc))
def test_group_already_exists_skip_saving_it(s3_raw_lake, group_db):
    WhatsAppGroup(
        "group-id", name="group-name", requires_daily_summary=SummaryStatus.MYSELF
    ).save()
    handler({}, MagicMock())

    groups = WhatsAppGroup.scan()
    assert list(groups)[0].requires_daily_summary == SummaryStatus.MYSELF
