import logging
from typing import Dict, Any, Optional
from ai.groq_client import groq_client

logger = logging.getLogger(__name__)


class SoftwareAccessEvaluator:
    """
    AI-driven Enterprise Software Access Governance Evaluator.
    Analyzes software requests against the employee's official job designation, department,
    and business justification, providing automated approval or flagging for manager/security review.
    """

    SYSTEM_PROMPT = """You are an Enterprise IT Software Access & Compliance AI Auditor.
Evaluate whether a software provisioning request should be auto-approved, forwarded for Manager Review, or flagged for Security Review based on the employee's designation and department.

Rules:
1. Technical & Engineering roles (e.g. Software Engineer, Developer, DevOps, Data Scientist, Tech Lead) are pre-approved for developer tooling (e.g. VS Code, Python, Docker, Postman, Git, compilers).
2. Design & Creative roles (e.g. UI/UX Designer, Product Designer) are pre-approved for creative and prototyping tools (e.g. Figma, Miro, Sketch).
3. Universal collaboration tools (e.g. Microsoft Teams, Slack, Zoom, Chrome) are pre-approved for all employees.
4. If an employee requests software outside their functional domain (e.g., an HR Specialist or Marketing Intern requesting Docker or AWS Admin CLI), flag it for "manager_review".
5. High-privilege, admin-level, or sensitive access tools must be flagged for "security_review".

Respond ONLY with valid JSON conforming to this schema:
{
  "recommendation": "auto_approved" | "manager_review" | "security_review",
  "status": "approved" | "pending_approval",
  "confidence": float (between 0.0 and 1.0),
  "designation_assessed": "string (the designation assessed)",
  "ai_rationale": "Clear 1-2 sentence explanation of why this software is either auto-approved or routed for manager review based on the employee's designation and department."
}
"""

    @classmethod
    def evaluate_request(
        cls,
        software: Dict[str, Any],
        user: Dict[str, Any],
        justification: str = "",
        designation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates a software request using Groq AI with deterministic rule fallback.
        """
        user_name = user.get("full_name") or user.get("email", "Employee")
        dept = user.get("department", "General")
        role = user.get("role", "employee")

        # Determine effective designation
        effective_designation = (
            designation
            or user.get("designation")
            or cls._infer_designation_from_role(role, dept)
        )

        sw_name = software.get("name", "Unknown Software")
        sw_category = software.get("category", "General")

        # 1. Try Groq AI Evaluation
        if groq_client.is_configured():
            try:
                user_prompt = (
                    f"Employee Profile:\n"
                    f"- Full Name: {user_name}\n"
                    f"- Job Designation: {effective_designation}\n"
                    f"- Department: {dept}\n"
                    f"- System Role: {role}\n\n"
                    f"Software Item:\n"
                    f"- Name: {sw_name}\n"
                    f"- Category: {sw_category}\n"
                    f"- Approval Required by Catalog: {software.get('approval_required', True)}\n\n"
                    f"Employee Business Justification:\n"
                    f"\"{justification or 'Standard corporate workstation software installation'}\""
                )

                res = groq_client.chat_json(
                    messages=[
                        {"role": "system", "content": cls.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.0,
                )

                rec = res.get("recommendation", "manager_review")
                status = "approved" if rec == "auto_approved" else "pending_approval"
                rationale = res.get(
                    "ai_rationale",
                    f"Request evaluated by AI for {effective_designation} in {dept}."
                )

                logger.info(f"AI Software Evaluation for '{sw_name}' by '{effective_designation}': {rec}")
                return {
                    "recommendation": rec,
                    "status": status,
                    "confidence": float(res.get("confidence", 0.92)),
                    "designation_assessed": effective_designation,
                    "ai_rationale": rationale,
                    "evaluated_by": "Groq GPT-OSS",
                }
            except Exception as e:
                logger.warning(f"Groq software evaluation failed: {e}. Falling back to rule-based evaluation.")

        # 2. Deterministic Rule-Based Fallback
        return cls._rule_based_evaluation(sw_name, sw_category, effective_designation, dept, justification)

    @classmethod
    def _infer_designation_from_role(cls, role: str, dept: str) -> str:
        if role == "admin":
            return "Senior IT Operations Director"
        elif role == "it_agent":
            return "IT Support Specialist"
        elif "engin" in dept.lower() or "tech" in dept.lower():
            return "Software Engineer"
        elif "design" in dept.lower():
            return "UI/UX Designer"
        elif "sales" in dept.lower():
            return "Sales Executive"
        elif "market" in dept.lower():
            return "Marketing Specialist"
        elif "hr" in dept.lower() or "people" in dept.lower():
            return "HR Specialist"
        return "Corporate Associate"

    @classmethod
    def _rule_based_evaluation(
        cls,
        sw_name: str,
        category: str,
        designation: str,
        dept: str,
        justification: str
    ) -> Dict[str, Any]:
        """High-precision fallback heuristic evaluation."""
        desig_lower = designation.lower()
        dept_lower = dept.lower()
        sw_lower = sw_name.lower()
        cat_lower = category.lower()

        is_tech_role = any(k in desig_lower or k in dept_lower for k in [
            "engineer", "developer", "devops", "architect", "programmer", "data", "qa", "test", "sre", "tech"
        ])

        is_design_role = any(k in desig_lower or k in dept_lower for k in [
            "designer", "ui", "ux", "creative", "art"
        ])

        # Collaboration & Office suites: Universal auto-approval
        if any(k in sw_lower for k in ["teams", "slack", "zoom", "chrome", "edge", "notion"]):
            return {
                "recommendation": "auto_approved",
                "status": "approved",
                "confidence": 0.98,
                "designation_assessed": designation,
                "ai_rationale": f"Universal enterprise collaboration tool pre-approved for all {designation} personnel.",
                "evaluated_by": "Rule Engine",
            }

        # Developer tools: Auto-approved for Tech roles
        if any(k in sw_lower or k in cat_lower for k in ["vs code", "visual studio", "python", "docker", "postman", "git", "developer", "ide"]):
            if is_tech_role:
                return {
                    "recommendation": "auto_approved",
                    "status": "approved",
                    "confidence": 0.95,
                    "designation_assessed": designation,
                    "ai_rationale": f"Developer tool '{sw_name}' is standard baseline tooling for {designation} in {dept}.",
                    "evaluated_by": "Rule Engine",
                }
            else:
                return {
                    "recommendation": "manager_review",
                    "status": "pending_approval",
                    "confidence": 0.88,
                    "designation_assessed": designation,
                    "ai_rationale": f"Software '{sw_name}' is technical development tooling outside standard {designation} scope. Routed for Manager Review.",
                    "evaluated_by": "Rule Engine",
                }

        # Design tools
        if any(k in sw_lower for k in ["figma", "adobe", "sketch"]):
            if is_design_role:
                return {
                    "recommendation": "auto_approved",
                    "status": "approved",
                    "confidence": 0.95,
                    "designation_assessed": designation,
                    "ai_rationale": f"Prototyping suite '{sw_name}' is standard tooling for {designation}.",
                    "evaluated_by": "Rule Engine",
                }
            else:
                return {
                    "recommendation": "manager_review",
                    "status": "pending_approval",
                    "confidence": 0.85,
                    "designation_assessed": designation,
                    "ai_rationale": f"High-tier design license for '{sw_name}' requires departmental approval for {designation}.",
                    "evaluated_by": "Rule Engine",
                }

        # Default fallback
        return {
            "recommendation": "manager_review",
            "status": "pending_approval",
            "confidence": 0.80,
            "designation_assessed": designation,
            "ai_rationale": f"Standard workflow: License allocation for '{sw_name}' requires review for {designation}.",
            "evaluated_by": "Rule Engine",
        }
