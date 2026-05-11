import requests
from config import Config

SUPABASE_URL = Config.SUPABASE_URL
SERVICE_KEY = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

_session = requests.Session()
_session.headers.update(HEADERS)

def get_user_by_id(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=*"
        res = _session.get(url, timeout=8)
        data = res.json()
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"get_user_by_id error: {e}")
        return None

def create_user_profile(user_id, name, email, phone='', address=''):
    try:
        payload = {
            "id": user_id, "name": name, "email": email,
            "phone": phone, "address": address, "is_admin": False
        }
        res = _session.post(f"{SUPABASE_URL}/rest/v1/users", json=payload, timeout=8)
        return res.json() if res.status_code in [200, 201] else None
    except Exception as e:
        print(f"create_user_profile error: {e}")
        return None

def update_user_profile(user_id, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        res = _session.patch(url, json=data, timeout=8)
        return True if res.status_code in [200, 201, 204] else None
    except Exception as e:
        print(f"update_user_profile error: {e}")
        return None
