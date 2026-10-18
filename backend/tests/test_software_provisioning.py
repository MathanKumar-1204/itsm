import pytest
from services.software_service import SoftwareService
from repositories.db_repository import db


def test_software_catalog_retrieval():
    catalog = SoftwareService.list_catalog(enabled_only=True)
    assert len(catalog) >= 3
    names = [s["name"] for s in catalog]
    assert "Visual Studio Code" in names
    assert "Docker Desktop Enterprise" in names


def test_preapproved_software_request_workflow():
    employee = {"id": "emp-test-42", "role": "employee"}
    # Visual Studio Code has approval_required = False
    vscode_item = next(s for s in SoftwareService.list_catalog() if s["name"] == "Visual Studio Code")

    req = SoftwareService.create_request(
        software_id=vscode_item["id"],
        justification="Need VS Code for frontend bug fixing",
        user=employee,
    )

    assert req["id"] is not None
    assert req["request_number"].startswith("SR-")
    assert req["status"] == "completed" # Pre-approved executes automatically
    assert req["provisioning_status"] == "completed"
    assert req["external_record_id"].startswith("SIM-DEPLOY-")


def test_approval_required_software_request_and_rbac():
    employee = {"id": "emp-test-43", "role": "employee"}
    admin = {"id": "admin-101", "role": "admin"}

    # Docker Desktop has approval_required = True
    docker_item = next(s for s in SoftwareService.list_catalog() if s["name"] == "Docker Desktop Enterprise")

    req = SoftwareService.create_request(
        software_id=docker_item["id"],
        justification="Required for microservices container testing",
        user=employee,
    )

    assert req["status"] == "pending_approval"
    assert req["provisioning_status"] == "pending"

    # Employee cannot self-approve
    with pytest.raises(PermissionError):
        SoftwareService.approve_request(req["id"], comment="I approve myself", user=employee)

    # Admin approves
    approved_req = SoftwareService.approve_request(req["id"], comment="Approved for Q4 engineering sprint", user=admin)
    assert approved_req["status"] == "completed"
    assert approved_req["approved_by"] == "admin-101"
    assert approved_req["provisioning_status"] == "completed"
