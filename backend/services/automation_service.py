import logging
from typing import Dict, Any, List, Optional
from automation.workflows import SelfHealEngine
from repositories.db_repository import db

logger = logging.getLogger(__name__)


class AutomationService:
    @classmethod
    def list_workflows(cls) -> List[Dict[str, Any]]:
        return SelfHealEngine.list_available_workflows()

    @classmethod
    def run_workflow(
        cls,
        workflow_name: str,
        issue_description: str,
        user: Dict[str, Any],
        ticket_id: Optional[str] = None,
        step_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return SelfHealEngine.execute_workflow(
            workflow_name=workflow_name,
            issue_description=issue_description,
            user=user,
            ticket_id=ticket_id,
            step_inputs=step_inputs,
        )

    @classmethod
    def list_runs(cls, user: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        user_role = user.get("role", "employee")
        user_id = user.get("id")
        # Employees see their own runs; IT staff see all
        filter_user_id = user_id if user_role == "employee" else None
        return db.list_automation_runs(user_id=filter_user_id, limit=limit)

    @classmethod
    def get_run(cls, run_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        run = db.get_automation_run(run_id)
        if not run:
            raise ValueError(f"Automation run '{run_id}' not found.")

        user_role = user.get("role", "employee")
        user_id = user.get("id")
        if user_role == "employee" and run.get("initiated_by") != user_id:
            raise PermissionError("Access denied.")
        return run

    @classmethod
    def verify_resolution(cls, run_id: str, resolved: bool, user: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        return SelfHealEngine.verify_resolution(
            run_id=run_id,
            resolved=resolved,
            user=user,
            feedback=feedback,
        )
