import pytest
from pydantic import ValidationError
from models.schemas import TicketCreateRequest, TicketClassifyRequest
from services.ticket_service import TicketService
from repositories.db_repository import db


def test_ticket_schema_validation():
    # Valid schema
    req = TicketCreateRequest(
        title="Wi-Fi Disconnecting Constantly",
        description="The corporate laptop loses 5GHz Wi-Fi every 10 minutes.",
        category="Network",
        impact="medium",
        urgency="high",
    )
    assert req.title == "Wi-Fi Disconnecting Constantly"
    assert req.category == "Network"

    # Invalid category should fail validation
    with pytest.raises(ValidationError):
        TicketCreateRequest(
            title="Valid Title",
            description="Valid Description",
            category="NonExistentCategory",
        )

    # Title too short should fail
    with pytest.raises(ValidationError):
        TicketCreateRequest(
            title="Hi",
            description="Valid Description",
            category="Hardware",
        )


def test_ticket_creation_and_ownership_enforcement():
    employee_user = {
        "id": "employee-1234",
        "email": "employee@enterprise.com",
        "role": "employee",
    }
    other_employee = {
        "id": "employee-5678",
        "email": "other@enterprise.com",
        "role": "employee",
    }
    staff_user = {
        "id": "agent-9999",
        "email": "agent@enterprise.com",
        "role": "it_agent",
    }

    # Create ticket as employee
    ticket_data = {
        "title": "VPN Authentication Failure",
        "description": "Error 403 when connecting to GlobalProtect gateway.",
        "category": "Network",
        "impact": "high",
        "urgency": "critical",
    }
    created = TicketService.create_ticket(ticket_data, user=employee_user)

    assert created["id"] is not None
    assert created["ticket_number"].startswith("INC-")
    assert created["requester_id"] == "employee-1234"
    assert created["priority"] == "critical" # high + critical = critical

    # Owner can view ticket
    fetched = TicketService.get_ticket(created["id"], user=employee_user)
    assert fetched["id"] == created["id"]

    # IT staff can view ticket
    staff_view = TicketService.get_ticket(created["id"], user=staff_user)
    assert staff_view["id"] == created["id"]

    # Other employee CANNOT view ticket (ownership check)
    with pytest.raises(PermissionError):
        TicketService.get_ticket(created["id"], user=other_employee)


def test_ticket_resolution_role_authorization():
    employee_user = {"id": "emp-1", "role": "employee"}
    agent_user = {"id": "agent-1", "role": "it_agent"}

    ticket = TicketService.create_ticket({
        "title": "Monitor flickering",
        "description": "Second screen goes black intermittently",
        "category": "Hardware",
        "impact": "low",
        "urgency": "low",
    }, user=employee_user)

    # Employee cannot resolve ticket
    with pytest.raises(PermissionError):
        TicketService.resolve_ticket(ticket["id"], "Replaced HDMI cable", user=employee_user)

    # IT Agent can resolve ticket
    resolved = TicketService.resolve_ticket(ticket["id"], "Replaced HDMI cable", user=agent_user)
    assert resolved["status"] == "resolved"
    assert resolved["resolution"] == "Replaced HDMI cable"
    assert resolved["resolved_at"] is not None
