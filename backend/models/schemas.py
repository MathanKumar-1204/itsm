from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, EmailStr


class TicketClassifyRequest(BaseModel):
    user_query: str = Field(..., min_length=3, description="Natural language problem description")
    requester_email: Optional[str] = None


class TicketClassificationResponse(BaseModel):
    title: str
    description: str
    category: Literal[
        "Hardware",
        "Network",
        "Software",
        "Account and Access",
        "Email",
        "Security",
        "General IT",
    ]
    ticket_type: Literal["incident", "service_request"] = "incident"
    impact: Literal["low", "medium", "high", "critical"]
    urgency: Literal["low", "medium", "high", "critical"]
    suggested_priority: Literal["low", "medium", "high", "critical"]
    calculated_priority: Literal["low", "medium", "high", "critical"]
    symptoms: List[str] = Field(default_factory=list)
    affected_service: Optional[str] = None
    suggested_troubleshooting_workflow: Optional[str] = None
    missing_information: List[str] = Field(default_factory=list)
    suggested_resolution: Optional[str] = None
    ai_confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class TicketCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    category: Literal[
        "Hardware",
        "Network",
        "Software",
        "Account and Access",
        "Email",
        "Security",
        "General IT",
    ]
    ticket_type: Literal["incident", "service_request"] = "incident"
    impact: Literal["low", "medium", "high", "critical"] = "medium"
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    ai_summary: Optional[str] = None
    ai_confidence: Optional[float] = None
    source: str = "portal"


class TicketUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Literal[
        "Hardware",
        "Network",
        "Software",
        "Account and Access",
        "Email",
        "Security",
        "General IT",
    ]] = None
    impact: Optional[Literal["low", "medium", "high", "critical"]] = None
    urgency: Optional[Literal["low", "medium", "high", "critical"]] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[Literal["new", "open", "in_progress", "pending", "resolved", "closed"]] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class TicketCommentCreateRequest(BaseModel):
    comment: str = Field(..., min_length=1)
    visibility: Literal["public", "internal"] = "public"


class TicketResolveRequest(BaseModel):
    resolution: str = Field(..., min_length=5)


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=4, ge=1, le=10)
    category: Optional[str] = None


class KnowledgeArticleGenerateRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1)


class KnowledgeArticleUpdateRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    status: Optional[Literal["draft", "pending_review", "published", "rejected"]] = None


class SoftwareRequestCreate(BaseModel):
    software_id: str = Field(..., min_length=1)
    business_justification: str = Field(..., min_length=3)
    designation: Optional[str] = None


class SoftwareRequestEvaluate(BaseModel):
    software_id: str = Field(..., min_length=1)
    business_justification: Optional[str] = ""
    designation: Optional[str] = None


class SoftwareRequestApprove(BaseModel):
    approved: bool
    approval_comment: Optional[str] = None


class AutomationRunRequest(BaseModel):
    workflow_name: str = Field(..., min_length=2)
    issue_description: str = Field(..., min_length=2)
    ticket_id: Optional[str] = None
    step_inputs: Optional[Dict[str, Any]] = None


class AutomationVerifyRequest(BaseModel):
    resolved: bool
    feedback: Optional[str] = None
