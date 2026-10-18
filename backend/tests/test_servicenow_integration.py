import pytest
from unittest.mock import patch, MagicMock
from integrations.servicenow import ServiceNowClient
from services.ticket_service import TicketService


def test_servicenow_demo_mode_incident_creation():
    client = ServiceNowClient()
    # Force demo mode
    client.demo_mode = True

    sample_ticket = {
        "id": "12345678-aaaa-bbbb-cccc-dddddddddddd",
        "ticket_number": "INC-1099",
        "title": "VPN connection drops after 5 minutes",
        "description": "User experiences TLS handshake timeouts",
        "category": "Network",
        "impact": "high",
        "urgency": "high",
    }

    res = client.create_incident(sample_ticket)
    assert res["success"] is True
    assert res["is_simulated"] is True
    assert "DEMO-INC-1099" in res["external_record_id"]
    assert "Demo Mode" in res["external_system"]


def test_servicenow_status_mapping_demo_mode():
    client = ServiceNowClient()
    client.demo_mode = True

    status_res = client.sync_incident_status("DEMO-INC-1099")
    assert status_res["success"] is True
    assert status_res["mapped_internal_status"] in ["in_progress", "open", "resolved"]


def test_servicenow_failure_does_not_fail_internal_ticket():
    user = {"id": "emp-test-99", "role": "employee"}

    # Mock ServiceNow client to simulate connection timeout/error
    with patch("services.ticket_service.servicenow_client.create_incident") as mock_sn:
        mock_sn.return_value = {
            "success": False,
            "error": "HTTP 503 Service Unavailable",
            "status": "sync_failed",
        }

        ticket = TicketService.create_ticket({
            "title": "Printer paper jam on 3rd floor",
            "description": "Tray 2 is jammed and red error light is on.",
            "category": "Hardware",
            "impact": "low",
            "urgency": "low",
        }, user=user)

        # Internal ticket MUST still be successfully created in the system!
        assert ticket["id"] is not None
        assert ticket["ticket_number"].startswith("INC-")
        assert ticket["status"] == "new"
        assert ticket["external_system"] == "ServiceNow (Sync Failed)"
