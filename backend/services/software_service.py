import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from repositories.db_repository import db
from integrations.servicenow import servicenow_client
from ai.software_evaluator import SoftwareAccessEvaluator

logger = logging.getLogger(__name__)


class SoftwareService:
    @classmethod
    def list_catalog(cls, enabled_only: bool = True) -> List[Dict[str, Any]]:
        return db.list_software_catalog(enabled_only=enabled_only)

    @classmethod
    def evaluate_request(
        cls,
        software_id: str,
        user: Dict[str, Any],
        justification: str = "",
        designation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pre-evaluates a software request using AI governance before submission."""
        software = db.get_software_item(software_id)
        if not software:
            raise ValueError(f"Software item '{software_id}' not found.")
        return SoftwareAccessEvaluator.evaluate_request(
            software=software,
            user=user,
            justification=justification,
            designation=designation
        )

    @classmethod
    def create_request(
        cls,
        software_id: str,
        justification: str,
        user: Dict[str, Any],
        designation: Optional[str] = None
    ) -> Dict[str, Any]:
        user_id = user["id"]
        software = db.get_software_item(software_id)
        if not software:
            raise ValueError(f"Software item '{software_id}' not found in catalogue.")

        if not software.get("enabled", True):
            raise ValueError(f"Software '{software.get('name')}' is currently disabled in the catalogue.")

        provisioning_mode = software.get("provisioning_mode", "simulated")

        # Execute AI Access Governance evaluation based on employee designation
        evaluation = SoftwareAccessEvaluator.evaluate_request(
            software=software,
            user=user,
            justification=justification,
            designation=designation
        )

        is_catalog_preapproved = not software.get("approval_required", True)
        is_auto_approved = is_catalog_preapproved or evaluation.get("recommendation") == "auto_approved" or evaluation.get("status") == "approved"
        initial_status = "approved" if is_auto_approved else "pending_approval"
        prov_status = "provisioning" if is_auto_approved else "pending"

        approved_by = (
            "PRE_APPROVED_CATALOG"
            if is_catalog_preapproved
            else f"AI_AUTO_APPROVAL ({evaluation.get('designation_assessed')})"
            if is_auto_approved
            else None
        )
        approval_comment = evaluation.get("ai_rationale")

        req_data = {
            "requester_id": user_id,
            "requester_name": user.get("full_name") or user.get("email", "Employee"),
            "software_id": software_id,
            "software_name": software.get("name"),
            "business_justification": justification,
            "designation": evaluation.get("designation_assessed", user.get("designation", "Employee")),
            "department": user.get("department", "General"),
            "ai_evaluation": evaluation.get("ai_rationale"),
            "ai_recommendation": evaluation.get("recommendation"),
            "ai_confidence": evaluation.get("confidence", 0.9),
            "status": initial_status,
            "provisioning_status": prov_status,
            "execution_mode": provisioning_mode,
            "approved_by": approved_by,
            "approval_comment": approval_comment,
        }

        # Create record in database
        req = db.create_software_request(req_data)
        req_id = req["id"]

        # If auto-approved by AI, automatically execute provisioning
        if is_auto_approved:
            cls.execute_provisioning(req_id, user)
            req = db.get_software_request(req_id)

        db.log_audit(
            actor_id=user_id,
            action="submit_software_request",
            entity_type="software_request",
            entity_id=req_id,
            metadata={
                "software_name": software.get("name"),
                "status": req.get("status"),
                "ai_recommendation": evaluation.get("recommendation"),
                "designation": evaluation.get("designation_assessed"),
            },
        )

        return req

    @classmethod
    def list_requests(cls, user: Dict[str, Any]) -> List[Dict[str, Any]]:
        user_role = user.get("role", "employee")
        user_id = user.get("id")
        filter_user_id = user_id if user_role == "employee" else None
        return db.list_software_requests(requester_id=filter_user_id)

    @classmethod
    def get_request(cls, request_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        req = db.get_software_request(request_id)
        if not req:
            raise ValueError(f"Software request '{request_id}' not found.")

        user_role = user.get("role", "employee")
        user_id = user.get("id")
        if user_role == "employee" and req.get("requester_id") != user_id:
            raise PermissionError("Access denied.")
        return req

    @classmethod
    def approve_request(cls, request_id: str, comment: Optional[str], user: Dict[str, Any]) -> Dict[str, Any]:
        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff and administrators can approve software requests.")

        req = db.get_software_request(request_id)
        if not req:
            raise ValueError(f"Software request '{request_id}' not found.")

        if req.get("status") not in ["submitted", "pending_approval"]:
            raise ValueError(f"Cannot approve request currently in '{req.get('status')}' state.")

        updates = {
            "status": "approved",
            "approved_by": user["id"],
            "approval_comment": comment or "Approved by IT Administrator.",
            "provisioning_status": "provisioning",
        }
        updated = db.update_software_request(request_id, updates)

        # Trigger provisioning
        cls.execute_provisioning(request_id, user)

        db.log_audit(
            actor_id=user["id"],
            action="approve_software_request",
            entity_type="software_request",
            entity_id=request_id,
            metadata={"comment": comment},
        )
        return db.get_software_request(request_id)

    @classmethod
    def reject_request(cls, request_id: str, comment: Optional[str], user: Dict[str, Any]) -> Dict[str, Any]:
        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff and administrators can reject software requests.")

        req = db.get_software_request(request_id)
        if not req:
            raise ValueError(f"Software request '{request_id}' not found.")

        updates = {
            "status": "rejected",
            "approved_by": user["id"],
            "approval_comment": comment or "Rejected by IT Administrator.",
            "provisioning_status": "cancelled",
        }
        updated = db.update_software_request(request_id, updates)

        db.log_audit(
            actor_id=user["id"],
            action="reject_software_request",
            entity_type="software_request",
            entity_id=request_id,
            metadata={"comment": comment},
        )
        return updated

    @classmethod
    def execute_provisioning(cls, request_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        req = db.get_software_request(request_id)
        if not req:
            raise ValueError(f"Software request '{request_id}' not found.")

        now = datetime.now(timezone.utc).isoformat()
        mode = req.get("execution_mode", "simulated")

        if mode == "simulated":
            ext_id = f"SIM-DEPLOY-{request_id[:8]}"
            updates = {
                "status": "completed",
                "provisioning_status": "completed",
                "external_record_id": ext_id,
                "completed_at": now,
            }
        elif mode == "integrated":
            ext_id = f"M365-LIC-{request_id[:8]}"
            updates = {
                "status": "completed",
                "provisioning_status": "completed",
                "external_record_id": ext_id,
                "completed_at": now,
            }
        else: # manual
            updates = {
                "status": "in_progress",
                "provisioning_status": "manual_action_required",
            }

        updated = db.update_software_request(request_id, updates)

        db.log_audit(
            actor_id=user.get("id"),
            action="execute_software_provisioning",
            entity_type="software_request",
            entity_id=request_id,
            metadata={"mode": mode, "status": updates.get("status")},
        )
        return updated
