import pytest
from automation.workflows import SelfHealEngine
from automation.tool_registry import APPROVED_TOOLS


def test_available_workflows_registered():
    workflows = SelfHealEngine.list_available_workflows()
    names = [w["workflow_name"] for w in workflows]
    assert "Network Troubleshooting" in names
    assert "Disk Space and Performance Guidance" in names
    assert "Application Troubleshooting" in names


def test_network_troubleshooting_workflow_execution():
    user = {"id": "user-test-1", "role": "employee"}
    run = SelfHealEngine.execute_workflow(
        workflow_name="Network Troubleshooting",
        issue_description="VPN keeps disconnecting and cannot load intranet websites.",
        user=user,
    )

    assert run["id"] is not None
    assert run["workflow_name"] == "Network Troubleshooting"
    assert run["status"] == "completed"
    assert run["execution_mode"] in ["real", "guided", "simulated"]
    assert len(run["steps"]) >= 4

    # Verify steps contain tool results
    step_names = [s["step_name"] for s in run["steps"]]
    assert "Classify Issue" in step_names
    assert "Retrieve Knowledge" in step_names
    assert "DNS Connectivity Probe" in step_names
    assert "Verification" in step_names


def test_verification_unresolved_escalation():
    user = {"id": "user-test-1", "role": "employee"}
    run = SelfHealEngine.execute_workflow(
        workflow_name="Application Troubleshooting",
        issue_description="Microsoft Teams crashes repeatedly on launch.",
        user=user,
    )

    # User reports problem is NOT resolved
    verify_res = SelfHealEngine.verify_resolution(
        run_id=run["id"],
        resolved=False,
        user=user,
        feedback="Still crashing after cache reset.",
    )

    assert verify_res["resolved"] is False
    assert verify_res["escalation_recommended"] is True
    assert verify_res["run"]["status"] == "failed"
    assert "Still crashing" in verify_res["run"]["result_summary"]
