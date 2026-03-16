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

def get_cart_items(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&select=*,products(*)"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_cart_items error: {e}")
        return []

def add_to_cart(user_id, product_id, quantity=1):
    try:
        # Check if exists
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
        res = requests.get(url, headers=HEADERS)
        existing = res.json()
        if existing and isinstance(existing, list) and len(existing) > 0:
            new_qty = existing[0]['quantity'] + quantity
            patch_url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
            requests.patch(patch_url, json={"quantity": new_qty}, headers=HEADERS)
        else:
            post_url = f"{SUPABASE_URL}/rest/v1/cart"
            requests.post(post_url, json={"user_id": user_id, "product_id": product_id, "quantity": quantity}, headers=HEADERS)
        return True
    except Exception as e:
        print(f"add_to_cart error: {e}")
        return False

def update_cart_quantity(user_id, product_id, quantity):
    try:
        if quantity <= 0:
            url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
            requests.delete(url, headers=HEADERS)
        else:
            url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
            requests.patch(url, json={"quantity": quantity}, headers=HEADERS)
        return True
    except Exception as e:
        return False

def remove_from_cart(user_id, product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&product_id=eq.{product_id}"
        requests.delete(url, headers=HEADERS)
        return True
    except Exception as e:
        return False

def clear_cart(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}"
        requests.delete(url, headers=HEADERS)
        return True
    except Exception as e:
        return False

def get_cart_count(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/cart?user_id=eq.{user_id}&select=quantity"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        if isinstance(data, list):
            return sum(item.get('quantity', 0) for item in data)
        return 0
    except Exception as e:
        return 0

def get_wishlist(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/wishlist?user_id=eq.{user_id}&select=*,products(*)"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        return []

def add_to_wishlist(user_id, product_id):
    try:
        check_url = f"{SUPABASE_URL}/rest/v1/wishlist?user_id=eq.{user_id}&product_id=eq.{product_id}"
        res = requests.get(check_url, headers=HEADERS)
        if not res.json():
            url = f"{SUPABASE_URL}/rest/v1/wishlist"
            requests.post(url, json={"user_id": user_id, "product_id": product_id}, headers=HEADERS)
        return True
    except Exception as e:
        return False

def remove_from_wishlist(user_id, product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/wishlist?user_id=eq.{user_id}&product_id=eq.{product_id}"
        requests.delete(url, headers=HEADERS)
        return True
    except Exception as e:
        return False

