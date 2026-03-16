import uuid
import json
import requests
from datetime import datetime
from config import Config

SUPABASE_URL = Config.SUPABASE_URL
SERVICE_KEY = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def create_order(user_id, items, total_price, delivery_type, delivery_address='',
                 delivery_time_slot='', payment_method='online', notes=''):
    try:
        order_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'items': json.dumps(items),
            'total_price': float(total_price),
            'payment_status': 'pending',
            'payment_method': payment_method,
            'delivery_type': delivery_type,
            'delivery_address': delivery_address,
            'delivery_time_slot': delivery_time_slot,
            'order_status': 'Order Placed',
            'notes': notes,
            'created_at': datetime.utcnow().isoformat()
        }
        url = f"{SUPABASE_URL}/rest/v1/orders"
        res = requests.post(url, json=order_data, headers=HEADERS)
        if res.status_code in [200, 201]:
            data = res.json()
            return data[0] if isinstance(data, list) else data
        else:
            print(f"create_order error: {res.text}")
            return None
    except Exception as e:
        print(f"create_order error: {e}")
        return None

def get_user_orders(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/orders?user_id=eq.{user_id}&order=created_at.desc"
        res = requests.get(url, headers=HEADERS)
        orders = res.json() if res.status_code == 200 else []
        for order in orders:
            order['items'] = safe_parse_items(order)
        return orders
    except Exception as e:
        print(f"get_user_orders error: {e}")
        return []

def get_order_by_id(order_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/orders?id=eq.{order_id}&select=*"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        if data and isinstance(data, list) and len(data) > 0:
            order = data[0]
            order['items'] = safe_parse_items(order)
            return order
        return None
    except Exception as e:
        return None

def safe_parse_items(order):
    """Safely parse order items from JSON string to list"""
    items = order.get('items', [])
    if isinstance(items, list):
        return items
    if isinstance(items, str):
        try:
            parsed = json.loads(items)
            return parsed if isinstance(parsed, list) else []
        except:
            return []
    return []

def update_order_status(order_id, status):
    try:
        url = f"{SUPABASE_URL}/rest/v1/orders?id=eq.{order_id}"
        requests.patch(url, json={"order_status": status}, headers=HEADERS)
        return True
    except Exception:
        return False

def update_payment_status(order_id, payment_status, razorpay_payment_id=None, razorpay_order_id=None):
    try:
        data = {"payment_status": payment_status}
        if razorpay_payment_id:
            data['razorpay_payment_id'] = razorpay_payment_id
        if razorpay_order_id:
            data['razorpay_order_id'] = razorpay_order_id
        if payment_status == 'paid':
            data['order_status'] = 'Payment Confirmed'
        url = f"{SUPABASE_URL}/rest/v1/orders?id=eq.{order_id}"
        requests.patch(url, json=data, headers=HEADERS)
        return True
    except Exception as e:
        print(f"update_payment_status error: {e}")
        return False

def get_all_orders(page=1, per_page=20):
    try:
        offset = (page - 1) * per_page
        url = f"{SUPABASE_URL}/rest/v1/orders?order=created_at.desc&limit={per_page}&offset={offset}"
        res = requests.get(url, headers=HEADERS)
        orders = res.json() if res.status_code == 200 else []
        for order in orders:
            order['items'] = safe_parse_items(order)
        return orders
    except Exception:
        return []

def count_orders():
    try:
        count_headers = {**HEADERS, "Prefer": "count=exact"}
        url = f"{SUPABASE_URL}/rest/v1/orders?select=id"
        res = requests.get(url, headers=count_headers)
        count = res.headers.get('content-range', '0/0').split('/')[-1]
        return int(count) if count.isdigit() else 0
    except Exception:
        return 0

def get_revenue_stats():
    try:
        url = f"{SUPABASE_URL}/rest/v1/orders?payment_status=eq.paid&select=total_price"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        if isinstance(data, list):
            return sum(float(o.get('total_price', 0)) for o in data)
        return 0
    except Exception:
        return 0

