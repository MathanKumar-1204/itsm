"""
Deprecated: The platform has migrated exclusively to MongoDB Cloud Atlas.
This stub exists for backward compatibility and returns None for all calls.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_supabase_admin_client():
    return None


def get_supabase_client(access_token: Optional[str] = None):
    return None
