from ...src.admin_panel.functions.agent_status.app import handler
from unittest.mock import MagicMock
from backend.src.utils.db_models.application_state import ApplicationState, ClientStatus


def test_status_arrives_update_db(application_state_db):
    request = {
        "version": "0",
        "id": "cb1a0ee2-7da9-9415-390b-6e87e86f5b56",
        "detail-type": "status-change",
        "source": "whatsapp-client",
        "account": "201893381538",
        "time": "2023-02-15T22:26:13Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {"status": "Connected"},
    }

    handler(request, MagicMock())

    assert ApplicationState.get_client_status() == ClientStatus.CONNECTED
