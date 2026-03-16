from supabase import create_client, Client
from config import Config

_supabase_client = None
_supabase_admin_client = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    return _supabase_client

def get_supabase_admin() -> Client:
    global _supabase_admin_client
    if _supabase_admin_client is None:
        _supabase_admin_client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY
        )
    return _supabase_admin_client
