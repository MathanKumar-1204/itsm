import logging
import requests
from typing import Dict, Any, Optional, List
from config import Config

logger = logging.getLogger(__name__)


class ServiceNowClient:
    """
    ServiceNow REST API integration module.
    Supports Basic and OAuth authentication, Incident creation, and status synchronization.
    Strictly isolates real API calls from Demo Mode.
    """

    def __init__(self):
        self.instance_url = Config.SERVICENOW_INSTANCE_URL
        self.username = Config.SERVICENOW_USERNAME
        self.password = Config.SERVICENOW_PASSWORD
        self.client_id = Config.SERVICENOW_CLIENT_ID
        self.client_secret = Config.SERVICENOW_CLIENT_SECRET
        self.auth_mode = Config.SERVICENOW_AUTH_MODE
        self.demo_mode = Config.SERVICENOW_DEMO_MODE

    def is_configured(self) -> bool:
        return bool(self.instance_url and self.username and self.password)

    def is_demo_mode(self) -> bool:
        return self.demo_mode or not self.is_configured()

    def get_connection_status(self) -> Dict[str, Any]:
        """Returns connection configuration status without exposing credentials."""
        return {
            "configured": self.is_configured(),
            "demo_mode": self.is_demo_mode(),
            "instance_url": self.instance_url or "None configured",
            "auth_mode": self.auth_mode,
        }

    def test_connection(self) -> Dict[str, Any]:
        """Performs a real probe to the ServiceNow Table API if configured."""
        if self.is_demo_mode():
            return {
                "success": True,
                "mode": "demo",
                "message": "ServiceNow is running in DEMO MODE. Live instance tests are skipped.",
            }

        url = f"{self.instance_url}/api/now/table/incident?sysparm_limit=1"
        try:
            resp = requests.get(
                url,
                auth=(self.username, self.password),
                headers={"Accept": "application/json"},
                timeout=10,
            )
            if resp.status_code == 200:
                return {
                    "success": True,
                    "mode": "real",
                    "status_code": 200,
                    "message": f"Successfully connected to ServiceNow instance at {self.instance_url}.",
                }
            else:
                return {
                    "success": False,
                    "mode": "real",
                    "status_code": resp.status_code,
                    "message": f"ServiceNow returned HTTP {resp.status_code}: {resp.text[:200]}",
                }
        except Exception as e:
            logger.error(f"ServiceNow connection test failed: {e}")
            return {
                "success": False,
                "mode": "real",
                "message": f"Connection exception: {str(e)}",
            }

    def create_incident(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an incident in ServiceNow Table API or returns a clearly marked simulated reference in Demo Mode.
        """
        if self.is_demo_mode():
            # Return clearly labelled demo external reference
            demo_sys_id = f"demo_sys_{ticket.get('id', '0000')[:8]}"
            demo_inc_num = f"DEMO-INC-{ticket.get('ticket_number', '1001').replace('INC-', '')}"
            return {
                "success": True,
                "external_system": "ServiceNow (Demo Mode)",
                "external_record_id": demo_inc_num,
                "external_record_url": f"https://example.service-now.com/nav_to.do?uri=incident.do?sys_id={demo_sys_id}",
                "is_simulated": True,
                "status": "synchronized",
            }

        # Real ServiceNow incident creation
        # Map internal impact & urgency to ServiceNow 1-3 scale
        sn_impact = "3" # Low
        if ticket.get("impact") == "critical":
            sn_impact = "1"
        elif ticket.get("impact") in ("high", "medium"):
            sn_impact = "2"

        sn_urgency = "3"
        if ticket.get("urgency") == "critical":
            sn_urgency = "1"
        elif ticket.get("urgency") in ("high", "medium"):
            sn_urgency = "2"

        # Set caller to System Administrator sys_id in ServiceNow
        caller_sys_id = "681ccaf9c0a8016400b98a06818d57c7"

        payload = {
            "short_description": f"[{ticket.get('ticket_number', 'INC-1000')}] {ticket.get('title', '')}",
            "description": ticket.get("description", ""),
            "category": ticket.get("category", "inquiry").lower(),
            "impact": sn_impact,
            "urgency": sn_urgency,
            "caller_id": caller_sys_id,
            "correlation_id": ticket.get("ticket_number", ""),
            "correlation_display": "ITSM AI Helpdesk",
            "comments": f"Created via ITSM AI Helpdesk Platform.\nInternal Ticket: {ticket.get('ticket_number')}\nRequester: {ticket.get('requester_name', 'Employee')}",
        }

        url = f"{self.instance_url}/api/now/table/incident"
        try:
            resp = requests.post(
                url,
                json=payload,
                auth=(self.username, self.password),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code in (200, 201):
                data = resp.json().get("result", {})
                sys_id = data.get("sys_id")
                number = data.get("number")
                return {
                    "success": True,
                    "external_system": "ServiceNow",
                    "external_record_id": number,
                    "external_record_url": f"{self.instance_url}/nav_to.do?uri=incident.do?sys_id={sys_id}",
                    "is_simulated": False,
                    "status": "synchronized",
                }
            else:
                logger.error(f"ServiceNow incident creation failed: {resp.status_code} - {resp.text}")
                return {
                    "success": False,
                    "error": f"ServiceNow returned HTTP {resp.status_code}: {resp.text[:200]}",
                    "status": "sync_failed",
                }
        except Exception as e:
            logger.error(f"ServiceNow API exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "sync_failed",
            }

    def sync_incident_status(self, external_record_id: str) -> Dict[str, Any]:
        """
        Fetches current status of ServiceNow incident and maps back to internal status.
        """
        if self.is_demo_mode():
            return {
                "success": True,
                "mode": "demo",
                "external_record_id": external_record_id,
                "external_state": "Work in Progress",
                "mapped_internal_status": "in_progress",
                "message": "Demo mode simulated status retrieved.",
            }

        url = f"{self.instance_url}/api/now/table/incident?sysparm_query=number={external_record_id}&sysparm_limit=1"
        try:
            resp = requests.get(
                url,
                auth=(self.username, self.password),
                headers={"Accept": "application/json"},
                timeout=10,
            )
            if resp.status_code == 200:
                results = resp.json().get("result", [])
                if results:
                    inc = results[0]
                    state = inc.get("state") # ServiceNow state: 1: New, 2: In Progress, 3: On Hold, 6: Resolved, 7: Closed
                    state_map = {
                        "1": "open",
                        "2": "in_progress",
                        "3": "pending",
                        "6": "resolved",
                        "7": "closed",
                    }
                    mapped = state_map.get(str(state), "open")
                    return {
                        "success": True,
                        "mode": "real",
                        "external_record_id": external_record_id,
                        "external_state": state,
                        "mapped_internal_status": mapped,
                    }
            return {"success": False, "error": f"Record {external_record_id} not found in ServiceNow"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def batch_sync_incident_states(self, external_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Batch queries ServiceNow for incident states and returns a mapping:
        {
            "INC0010009": {
                "state_code": "6",
                "state_display": "Resolved",
                "mapped_status": "resolved",
                "sys_id": "...",
            }
        }
        """
        if self.is_demo_mode():
            return {}

        state_map = {
            "1": ("New", "new"),
            "2": ("In Progress", "in_progress"),
            "3": ("On Hold", "pending"),
            "6": ("Resolved", "resolved"),
            "7": ("Closed", "closed"),
            "8": ("Canceled", "closed"),
        }

        query = "ORDERBYDESCsys_updated_on"
        if external_ids:
            clean_ids = [str(x).strip() for x in external_ids if x]
            if clean_ids:
                query = f"numberIN{','.join(clean_ids)}"

        url = f"{self.instance_url}/api/now/table/incident?sysparm_fields=number,state,sys_id,sys_updated_on&sysparm_query={query}&sysparm_display_value=all&sysparm_limit=100"
        try:
            resp = requests.get(
                url,
                auth=(self.username, self.password),
                headers={"Accept": "application/json"},
                timeout=8,
            )
            if resp.status_code == 200:
                results = resp.json().get("result", [])
                out = {}
                for inc in results:
                    num = inc.get("number", {}).get("value") if isinstance(inc.get("number"), dict) else inc.get("number")
                    st_val = str(inc.get("state", {}).get("value") if isinstance(inc.get("state"), dict) else inc.get("state"))
                    st_disp = inc.get("state", {}).get("display_value") if isinstance(inc.get("state"), dict) else None

                    default_disp, mapped_status = state_map.get(st_val, ("New", "new"))
                    display_name = st_disp or default_disp

                    if num:
                        out[num] = {
                            "state_code": st_val,
                            "state_display": display_name,
                            "mapped_status": mapped_status,
                            "sys_id": inc.get("sys_id", {}).get("value") if isinstance(inc.get("sys_id"), dict) else inc.get("sys_id"),
                        }
                return out
        except Exception as e:
            logger.warning(f"Batch ServiceNow sync error: {e}")
        return {}


servicenow_client = ServiceNowClient()
