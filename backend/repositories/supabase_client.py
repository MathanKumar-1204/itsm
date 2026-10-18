import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

_supabase_admin_client = None
_supabase_anon_client = None


def get_supabase_admin_client():
    """Returns the privileged Supabase client using service role key (for backend trusted ops)."""
    global _supabase_admin_client
    if _supabase_admin_client is not None:
        return _supabase_admin_client

    if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase URL or Service Role Key not configured.")
        return None

    try:
        from supabase import create_client, Client
        _supabase_admin_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        return _supabase_admin_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        return None


def get_supabase_client(access_token: Optional[str] = None):
    """
    Returns a user-scoped Supabase client when access_token is provided,
    otherwise falls back to anon or admin client.
    """
    if not Config.SUPABASE_URL:
        return None

    try:
        from supabase import create_client, ClientOptions
        key = Config.SUPABASE_ANON_KEY or Config.SUPABASE_SERVICE_ROLE_KEY
        if not key:
            return None

        if access_token:
            options = ClientOptions(headers={"Authorization": f"Bearer {access_token}"})
            return create_client(Config.SUPABASE_URL, key, options=options)
        
        global _supabase_anon_client
        if _supabase_anon_client is None:
            _supabase_anon_client = create_client(Config.SUPABASE_URL, key)
        return _supabase_anon_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None
