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

def get_all_products(category=None, subcategory=None, search=None, page=1, per_page=12):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&order=created_at.desc"
        if category:
            url += f"&category=eq.{requests.utils.quote(category)}"
        if subcategory:
            url += f"&subcategory=eq.{requests.utils.quote(subcategory)}"
        if search:
            url += f"&name=ilike.*{requests.utils.quote(search)}*"
        offset = (page - 1) * per_page
        url += f"&limit={per_page}&offset={offset}"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_all_products error: {e}")
        return []

def get_product_by_id(product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}&select=*"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        return data[0] if data and isinstance(data, list) else None
    except Exception as e:
        print(f"get_product_by_id error: {e}")
        return None

def get_featured_products(limit=8):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&is_featured=eq.true&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_featured_products error: {e}")
        return []

def get_products_by_category(category, limit=6):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&category=eq.{requests.utils.quote(category)}&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_products_by_category error: {e}")
        return []

def create_product(data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products"
        res = requests.post(url, json=data, headers=HEADERS)
        return res.json() if res.status_code in [200, 201] else None
    except Exception as e:
        print(f"create_product error: {e}")
        return None

def update_product(product_id, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}"
        res = requests.patch(url, json=data, headers=HEADERS)
        return True if res.status_code in [200, 201, 204] else None
    except Exception as e:
        print(f"update_product error: {e}")
        return None

def delete_product(product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}"
        res = requests.patch(url, json={"is_active": False}, headers=HEADERS)
        return True
    except Exception as e:
        return False

def search_products(query, limit=10):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&name=ilike.*{requests.utils.quote(query)}*&select=id,name,price,discount,image_url&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        return []

def count_products():
    try:
        count_headers = {**HEADERS, "Prefer": "count=exact"}
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&select=id"
        res = requests.get(url, headers=count_headers)
        count = res.headers.get('content-range', '0/0').split('/')[-1]
        return int(count) if count.isdigit() else len(res.json())
    except Exception as e:
        return 0

# ── RECOMMENDATION FUNCTIONS ──────────────────────────────

def get_best_deals(limit=8):
    """Products with highest discount percentage"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&discount=gt.0&order=discount.desc&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_best_deals error: {e}")
        return []

def get_newly_added(limit=8):
    """Most recently added products"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&order=created_at.desc&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print(f"get_newly_added error: {e}")
        return []

def get_trending_products(limit=8):
    """Most ordered products based on order history"""
    try:
        import json
        # Get all paid/confirmed orders
        orders_url = f"{SUPABASE_URL}/rest/v1/orders?select=items&order=created_at.desc&limit=100"
        res = requests.get(orders_url, headers=HEADERS)
        orders = res.json() if res.status_code == 200 else []

        # Count product occurrences across all orders
        product_count = {}
        for order in orders:
            items = order.get('items', [])
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []
            for item in items:
                pid = item.get('product_id')
                qty = item.get('quantity', 1)
                if pid:
                    product_count[pid] = product_count.get(pid, 0) + qty

        if not product_count:
            # Fallback: return featured products if no orders yet
            return get_featured_products(limit=limit)

        # Sort by most ordered
        sorted_ids = sorted(product_count, key=product_count.get, reverse=True)[:limit]

        # Fetch those products
        trending = []
        for pid in sorted_ids:
            url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}&is_active=eq.true&select=*"
            r = requests.get(url, headers=HEADERS)
            data = r.json()
            if data and isinstance(data, list) and len(data) > 0:
                product = data[0]
                product['order_count'] = product_count[pid]
                trending.append(product)

        # If not enough trending, fill with featured
        if len(trending) < limit:
            featured = get_featured_products(limit=limit)
            existing_ids = {p['id'] for p in trending}
            for p in featured:
                if p['id'] not in existing_ids and len(trending) < limit:
                    trending.append(p)

        return trending
    except Exception as e:
        print(f"get_trending_products error: {e}")
        return get_featured_products(limit=limit)

def get_buy_again_products(user_id, limit=8):
    """Products the logged-in user has ordered before"""
    try:
        import json
        # Get this user's orders
        orders_url = f"{SUPABASE_URL}/rest/v1/orders?user_id=eq.{user_id}&order=created_at.desc&limit=20"
        res = requests.get(orders_url, headers=HEADERS)
        orders = res.json() if res.status_code == 200 else []

        if not orders:
            return []

        # Collect unique product IDs from past orders (most recent first)
        seen_ids = []
        seen_set = set()
        for order in orders:
            items = order.get('items', [])
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []
            for item in items:
                pid = item.get('product_id')
                if pid and pid not in seen_set:
                    seen_ids.append(pid)
                    seen_set.add(pid)
                if len(seen_ids) >= limit:
                    break
            if len(seen_ids) >= limit:
                break

        # Fetch those products
        buy_again = []
        for pid in seen_ids[:limit]:
            url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}&is_active=eq.true&select=*"
            r = requests.get(url, headers=HEADERS)
            data = r.json()
            if data and isinstance(data, list) and len(data) > 0:
                buy_again.append(data[0])

        return buy_again
    except Exception as e:
        print(f"get_buy_again_products error: {e}")
        return []


