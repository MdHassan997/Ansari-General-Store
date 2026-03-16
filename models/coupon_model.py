import requests
from config import Config
from datetime import datetime

SUPABASE_URL = Config.SUPABASE_URL
SERVICE_KEY = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_coupon_by_code(code):
    """Fetch a coupon by its code"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/coupons?code=eq.{code.upper()}&is_active=eq.true"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"get_coupon_by_code error: {e}")
        return None

def validate_coupon(code, subtotal, user_id=None):
    """
    Validate coupon and return discount details.
    Returns dict with:
      - valid: True/False
      - error: error message if invalid
      - discount_type: 'percentage' | 'fixed' | 'free_delivery'
      - discount_value: number
      - discount_amount: actual amount saved
      - new_delivery_charge: new delivery charge
    """
    coupon = get_coupon_by_code(code)

    if not coupon:
        return {'valid': False, 'error': 'Invalid coupon code'}

    # Check expiry
    if coupon.get('expires_at'):
        try:
            expiry = datetime.fromisoformat(coupon['expires_at'].replace('Z', '+00:00'))
            if expiry < datetime.now(expiry.tzinfo):
                return {'valid': False, 'error': 'Coupon has expired'}
        except:
            pass

    # Check minimum order amount
    min_order = float(coupon.get('min_order_amount', 0))
    if subtotal < min_order:
        return {
            'valid': False,
            'error': f'Minimum order amount ₹{min_order:.0f} required for this coupon'
        }

    # Check usage limit
    max_uses = coupon.get('max_uses')
    current_uses = int(coupon.get('used_count', 0))
    if max_uses and current_uses >= max_uses:
        return {'valid': False, 'error': 'Coupon usage limit reached'}

    # Calculate discount
    discount_type = coupon.get('discount_type', 'percentage')
    discount_value = float(coupon.get('discount_value', 0))
    delivery_charge = 40 if subtotal < 500 else 0
    discount_amount = 0
    new_delivery_charge = delivery_charge

    if discount_type == 'free_delivery':
        new_delivery_charge = 0
        discount_amount = delivery_charge
    elif discount_type == 'percentage':
        discount_amount = round(subtotal * discount_value / 100, 2)
        max_discount = coupon.get('max_discount_amount')
        if max_discount and discount_amount > float(max_discount):
            discount_amount = float(max_discount)
    elif discount_type == 'fixed':
        discount_amount = min(discount_value, subtotal)

    return {
        'valid': True,
        'coupon': coupon,
        'discount_type': discount_type,
        'discount_value': discount_value,
        'discount_amount': discount_amount,
        'new_delivery_charge': new_delivery_charge,
        'description': coupon.get('description', ''),
        'code': coupon.get('code', code.upper())
    }

def increment_coupon_usage(code):
    """Increment used_count when coupon is applied to an order"""
    try:
        coupon = get_coupon_by_code(code)
        if coupon:
            new_count = int(coupon.get('used_count', 0)) + 1
            url = f"{SUPABASE_URL}/rest/v1/coupons?code=eq.{code.upper()}"
            requests.patch(url, json={'used_count': new_count}, headers=HEADERS)
    except Exception as e:
        print(f"increment_coupon_usage error: {e}")

def get_all_coupons():
    """Admin: get all coupons"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/coupons?order=created_at.desc"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def create_coupon(data):
    """Admin: create a new coupon"""
    try:
        data['code'] = data['code'].upper().strip()
        url = f"{SUPABASE_URL}/rest/v1/coupons"
        res = requests.post(url, json=data, headers=HEADERS)
        return res.json() if res.status_code in [200, 201] else None
    except Exception as e:
        print(f"create_coupon error: {e}")
        return None

def update_coupon(coupon_id, data):
    """Admin: update a coupon"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/coupons?id=eq.{coupon_id}"
        res = requests.patch(url, json=data, headers=HEADERS)
        return True
    except Exception:
        return False

def delete_coupon(coupon_id):
    """Admin: deactivate a coupon"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/coupons?id=eq.{coupon_id}"
        requests.patch(url, json={'is_active': False}, headers=HEADERS)
        return True
    except Exception:
        return False
