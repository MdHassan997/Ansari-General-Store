import requests
from config import Config
from utils.cache import cache_get, cache_set, cache_delete

SUPABASE_URL = Config.SUPABASE_URL
SERVICE_KEY = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Shared session for connection reuse
_session = requests.Session()
_session.headers.update(HEADERS)

def _clear_cart_cache(user_id):
    cache_delete(f"cart_count:{user_id}")
    cache_delete(f"cart_items:{user_id}")

def get_cart_items(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&select=*,products(*)"
        res = _session.get(url, timeout=8)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_cart_items error: {e}")
        return []

def add_to_cart(user_id, product_id, quantity=1):
    try:
        check_url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
        res = _session.get(check_url, timeout=8)
        existing = res.json() if res.status_code == 200 else []
        if existing and isinstance(existing, list) and len(existing) > 0:
            new_qty = existing[0]['quantity'] + quantity
            _session.patch(check_url, json={"quantity": new_qty}, timeout=8)
        else:
            _session.post(f"{SUPABASE_URL}/rest/v1/cart",
                         json={"user_id": user_id, "product_id": product_id, "quantity": quantity},
                         timeout=8)
        _clear_cart_cache(user_id)
        return True
    except Exception as e:
        print(f"add_to_cart error: {e}")
        return False

def update_cart_quantity(user_id, product_id, quantity):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
        if quantity <= 0:
            _session.delete(url, timeout=8)
        else:
            _session.patch(url, json={"quantity": quantity}, timeout=8)
        _clear_cart_cache(user_id)
        return True
    except Exception as e:
        return False

def remove_from_cart(user_id, product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
        _session.delete(url, timeout=8)
        _clear_cart_cache(user_id)
        return True
    except Exception as e:
        return False

def clear_cart(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}"
        _session.delete(url, timeout=8)
        _clear_cart_cache(user_id)
        return True
    except Exception as e:
        return False

def get_cart_count(user_id):
    """Cached cart count — avoids hitting Supabase on every page load"""
    cache_key = f"cart_count:{user_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&select=quantity"
        res = _session.get(url, timeout=8)
        data = res.json() if res.status_code == 200 else []
        count = sum(item.get('quantity', 0) for item in (data if isinstance(data, list) else []))
        cache_set(cache_key, count, ttl=30)  # Cache for 30 seconds
        return count
    except Exception as e:
        return 0

def get_wishlist(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/wishlist?user_id=eq.{user_id}&select=*,products(*)"
        res = _session.get(url, timeout=8)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        return []

def add_to_wishlist(user_id, product_id):
    try:
        check_url = f"{SUPABASE_URL}/rest/v1/wishlist?user_id=eq.{user_id}&product_id=eq.{product_id}"
        res = _session.get(check_url, timeout=8)
        if not res.json():
            _session.post(f"{SUPABASE_URL}/rest/v1/wishlist",
                         json={"user_id": user_id, "product_id": product_id},
                         timeout=8)
        return True
    except Exception as e:
        return False

def remove_from_wishlist(user_id, product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/wishlist?user_id=eq.{user_id}&product_id=eq.{product_id}"
        _session.delete(url, timeout=8)
        return True
    except Exception as e:
        return False
