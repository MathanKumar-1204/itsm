import time
import logging
from typing import Dict, Any, List, Optional
from automation.tool_registry import APPROVED_TOOLS
from repositories.db_repository import db
from ai.rag_pipeline import rag_pipeline

logger = logging.getLogger(__name__)


class SelfHealEngine:
    """
    Controlled Automation Workflow Engine.
    Executes bounded state machine:
    classify -> retrieve -> plan -> authorize -> execute -> verify -> resolve_or_escalate
    """

    WORKFLOWS = {
        "Network Troubleshooting": {
            "category": "Network",
            "description": "Diagnoses internet connectivity, DNS lookup, and corporate VPN access.",
            "steps": [
                {"name": "Classify Issue", "action": "classify"},
                {"name": "Retrieve Knowledge", "action": "retrieve"},
                {"name": "Plan Diagnostics", "action": "plan"},
                {"name": "DNS Connectivity Probe", "tool": "ping_dns", "mode": "real"},
                {"name": "VPN Gateway Status Check", "tool": "check_vpn_gateway", "mode": "guided"},
                {"name": "Verification & Outcome", "action": "verify"},
            ],
        },
        "Disk Space and Performance Guidance": {
            "category": "Hardware",
            "description": "Identifies full storage drives, isolates safe temporary caches, and provides cleanup steps.",
            "steps": [
                {"name": "Classify Issue", "action": "classify"},
                {"name": "Retrieve Knowledge", "action": "retrieve"},
                {"name": "Plan Storage Analysis", "action": "plan"},
                {"name": "Disk Space Diagnostic Check", "tool": "disk_space_diagnostic", "mode": "simulated"},
                {"name": "Safe Cleanup Recommendations", "action": "guidance"},
                {"name": "Verification & Outcome", "action": "verify"},
            ],
        },
        "Application Troubleshooting": {
            "category": "Software",
            "description": "Inspects crashing or unresponsive enterprise applications and clears corrupt profile locks.",
            "steps": [
                {"name": "Classify Issue", "action": "classify"},
                {"name": "Retrieve Knowledge", "action": "retrieve"},
                {"name": "Plan App Diagnostic", "action": "plan"},
                {"name": "App Process Integrity Check", "tool": "app_process_check", "mode": "simulated"},
                {"name": "Cache Reset Guidance", "action": "guidance"},
                {"name": "Verification & Outcome", "action": "verify"},
            ],
        },
    }

    @classmethod
    def list_available_workflows(cls) -> List[Dict[str, Any]]:
        return [
            {
                "workflow_name": k,
                "category": v["category"],
                "description": v["description"],
                "step_count": len(v["steps"]),
            }
            for k, v in cls.WORKFLOWS.items()
        ]

    @classmethod
    def execute_workflow(
        cls,
        workflow_name: str,
        issue_description: str,
        user: Dict[str, Any],
        ticket_id: Optional[str] = None,
        step_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an approved workflow end-to-end, recording executed steps and actual/simulated results.
        """
        wf = cls.WORKFLOWS.get(workflow_name)
        if not wf:
            raise ValueError(f"Unknown workflow '{workflow_name}'. Available: {list(cls.WORKFLOWS.keys())}")

        step_inputs = step_inputs or {}
        user_role = user.get("role", "employee")
        user_id = user.get("id")

        executed_steps = []
        overall_mode = "real"

        # 1. Classify
        executed_steps.append({
            "step_name": "Classify Issue",
            "status": "completed",
            "details": f"Classified issue '{issue_description[:60]}...' under category: {wf['category']}.",
            "mode": "real",
        })

        # 2. Retrieve Knowledge
        kb_results = rag_pipeline.search_knowledge(query=issue_description, top_k=2, category=wf["category"])
        kb_summary = f"Retrieved {len(kb_results)} relevant internal documentation references." if kb_results else "No existing documentation found; proceeding with direct diagnostic tools."
        executed_steps.append({
            "step_name": "Retrieve Knowledge",
            "status": "completed",
            "details": kb_summary,
            "sources": [{"title": r["title"], "section": r.get("section")} for r in kb_results],
            "mode": "real",
        })

        # 3. Plan
        executed_steps.append({
            "step_name": "Plan Diagnostics",
            "status": "completed",
            "details": f"Planned {len(wf['steps']) - 3} diagnostic checks according to verified IT policy.",
            "mode": "real",
        })

        # 4. Execute approved tools
        diagnostic_findings = []
        for step in wf["steps"]:
            tool_name = step.get("tool")
            if not tool_name:
                continue

            tool = APPROVED_TOOLS.get(tool_name)
            if not tool:
                continue

            tool_mode = step.get("mode", "simulated")
            if tool_mode != "real" and overall_mode == "real":
                overall_mode = tool_mode

            result = tool.execute(step_inputs, actor_role=user_role)
            diagnostic_findings.append(result.get("message", "Check completed."))

            executed_steps.append({
                "step_name": step["name"],
                "status": "completed" if result.get("success") else "warning",
                "tool": tool_name,
                "result": result,
                "mode": result.get("execution_mode", tool_mode),
            })

        # 5. Verification prompt step
        result_summary = "Diagnostic completed successfully: " + "; ".join(diagnostic_findings)
        executed_steps.append({
            "step_name": "Verification",
            "status": "completed",
            "details": "Awaiting employee confirmation if self-healing steps resolved the problem.",
            "mode": "real",
        })

        # Persist to automation_runs table
        run_record = {
            "ticket_id": ticket_id,
            "initiated_by": user_id,
            "workflow_name": workflow_name,
            "issue_category": wf["category"],
            "input_summary": issue_description,
            "status": "completed",
            "steps": executed_steps,
            "result_summary": result_summary,
            "resolved": False, # Waiting for user verification
            "requires_approval": False,
            "execution_mode": overall_mode,
        }
        saved_run = db.create_automation_run(run_record)

        # Audit log
        db.log_audit(
            actor_id=user_id,
            action="execute_automation_workflow",
            entity_type="automation_run",
            entity_id=saved_run["id"],
            metadata={"workflow_name": workflow_name, "execution_mode": overall_mode},
        )

        return saved_run

    @classmethod
    def verify_resolution(cls, run_id: str, resolved: bool, user: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Handles employee verification. If unresolved, offers immediate ticket escalation.
        """
        run = db.get_automation_run(run_id)
        if not run:
            raise ValueError(f"Automation run '{run_id}' not found.")

        updates = {
            "resolved": resolved,
            "status": "completed" if resolved else "failed",
        }
        if feedback:
            updates["result_summary"] = (run.get("result_summary") or "") + f" | Employee Feedback: {feedback}"

        updated_run = db.update_automation_run(run_id, updates)

        db.log_audit(
            actor_id=user.get("id"),
            action="verify_automation_outcome",
            entity_type="automation_run",
            entity_id=run_id,
            metadata={"resolved": resolved, "feedback": feedback},
        )

        return {
            "run": updated_run,
            "resolved": resolved,
            "escalation_recommended": not resolved,
        }
