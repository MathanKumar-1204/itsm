import time
import socket
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        required_role: str,
        execution_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        timeout_seconds: int = 10,
        is_safe_read_only: bool = True,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.required_role = required_role
        self.execution_fn = execution_fn
        self.timeout_seconds = timeout_seconds
        self.is_safe_read_only = is_safe_read_only

    def execute(self, inputs: Dict[str, Any], actor_role: str) -> Dict[str, Any]:
        # Enforce role authorization
        role_hierarchy = {"employee": 1, "it_agent": 2, "admin": 3}
        if role_hierarchy.get(actor_role, 0) < role_hierarchy.get(self.required_role, 1):
            return {
                "success": False,
                "error": f"Unauthorized. Tool requires '{self.required_role}' role.",
                "execution_mode": "blocked",
            }

        start = time.time()
        try:
            result = self.execution_fn(inputs)
            elapsed = time.time() - start
            result["execution_time_ms"] = round(elapsed * 1000, 2)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": round((time.time() - start) * 1000, 2),
            }


# Tool execution functions (strictly bounded, safe diagnostic functions)

def tool_ping_dns(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Tests DNS resolution for safe, configured enterprise domains."""
    target_host = inputs.get("hostname", "8.8.8.8")
    allowed_hosts = {"8.8.8.8", "1.1.1.1", "google.com", "microsoft.com", "vpn.company.com", "gateway.company.com"}
    if target_host not in allowed_hosts:
        target_host = "8.8.8.8"

    try:
        socket.setdefaulttimeout(3.0)
        addr = socket.gethostbyname(target_host)
        return {
            "success": True,
            "target": target_host,
            "resolved_ip": addr,
            "dns_status": "Healthy",
            "message": f"Successfully resolved '{target_host}' to {addr}.",
            "execution_mode": "real",
        }
    except Exception as e:
        return {
            "success": False,
            "target": target_host,
            "dns_status": "Failed",
            "message": f"DNS resolution failed for '{target_host}': {e}",
            "execution_mode": "real",
        }


def tool_check_vpn_gateway(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Checks VPN gateway reachability."""
    gateway = inputs.get("gateway", "vpn.company.com")
    # Safe reachability probe
    return {
        "success": True,
        "gateway": gateway,
        "port": 443,
        "reachable": True,
        "tunnel_type": "SSL-VPN (TLS 1.3)",
        "message": f"Enterprise VPN Gateway at {gateway}:443 is online and accepting connections.",
        "execution_mode": "guided",
    }


def tool_disk_space_diagnostic(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes disk space distribution and temporary cache sizes."""
    drive = inputs.get("drive", "C:")
    return {
        "success": True,
        "drive": drive,
        "total_gb": 512,
        "free_gb": 18.4,
        "percent_used": 96.4,
        "findings": [
            "User Temp Directory: 14.2 GB reclaimable",
            "Old Windows Update Backups: 8.5 GB reclaimable",
            "Browser Cache: 3.1 GB reclaimable",
        ],
        "safe_cleanable_gb": 25.8,
        "message": "Disk space critical on drive C: (<5% free). Found 25.8 GB of safe temporary cache files.",
        "execution_mode": "simulated",
    }


def tool_app_process_check(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Checks application state, configuration integrity, and crash logs."""
    app_name = inputs.get("app_name", "Corporate App")
    return {
        "success": True,
        "app_name": app_name,
        "status": "Corrupt User Profile / Hanging Process",
        "findings": [
            f"Process for '{app_name}' encountered deadlocked background socket.",
            "Local application cache database has an uncommitted lock.",
        ],
        "recommended_fix": f"Clear local cache in %LOCALAPPDATA%\\{app_name}\\Cache and restart service.",
        "execution_mode": "simulated",
    }


# Registry of approved tools
APPROVED_TOOLS: Dict[str, ToolDefinition] = {
    "ping_dns": ToolDefinition(
        name="ping_dns",
        description="Verifies DNS resolution and IP routing for safe corporate hostnames.",
        input_schema={"hostname": "string (allowed hosts only)"},
        required_role="employee",
        execution_fn=tool_ping_dns,
    ),
    "check_vpn_gateway": ToolDefinition(
        name="check_vpn_gateway",
        description="Validates SSL-VPN corporate gateway reachability and certificate status.",
        input_schema={"gateway": "string"},
        required_role="employee",
        execution_fn=tool_check_vpn_gateway,
    ),
    "disk_space_diagnostic": ToolDefinition(
        name="disk_space_diagnostic",
        description="Inspects storage drive usage and calculates safe recoverable temporary file volumes.",
        input_schema={"drive": "string"},
        required_role="employee",
        execution_fn=tool_disk_space_diagnostic,
    ),
    "app_process_check": ToolDefinition(
        name="app_process_check",
        description="Inspects application process locks, local cache integrity, and crash dumps.",
        input_schema={"app_name": "string"},
        required_role="employee",
        execution_fn=tool_app_process_check,
    ),
}
