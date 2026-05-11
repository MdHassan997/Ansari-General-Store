import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import Config
from utils.cache import cache_get, cache_set, cache_clear_prefix

SUPABASE_URL = Config.SUPABASE_URL
SERVICE_KEY = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Shared requests session for connection reuse (much faster)
_session = requests.Session()
_session.headers.update(HEADERS)

def _get(url):
    """Make GET request with connection reuse"""
    try:
        res = _session.get(url, timeout=8)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"API error: {e}")
        return []

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
        return _get(url)
    except Exception as e:
        print(f"get_all_products error: {e}")
        return []

def get_product_by_id(product_id):
    cache_key = f"product:{product_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}&select=*"
        data = _get(url)
        result = data[0] if data and isinstance(data, list) else None
        if result:
            cache_set(cache_key, result, ttl=300)
        return result
    except Exception as e:
        print(f"get_product_by_id error: {e}")
        return None

def get_featured_products(limit=8):
    cache_key = f"featured:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&is_featured=eq.true&limit={limit}"
    result = _get(url)
    cache_set(cache_key, result, ttl=300)
    return result

def get_products_by_category(category, limit=6):
    cache_key = f"cat:{category}:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&category=eq.{requests.utils.quote(category)}&limit={limit}"
    result = _get(url)
    cache_set(cache_key, result, ttl=300)
    return result

def get_best_deals(limit=8):
    cache_key = f"deals:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&discount=gt.0&order=discount.desc&limit={limit}"
    result = _get(url)
    cache_set(cache_key, result, ttl=300)
    return result

def get_newly_added(limit=8):
    cache_key = f"new:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&order=created_at.desc&limit={limit}"
    result = _get(url)
    cache_set(cache_key, result, ttl=300)
    return result

def get_trending_products(limit=8):
    """Most ordered products — with fallback to featured"""
    cache_key = f"trending:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        import json
        orders_url = f"{SUPABASE_URL}/rest/v1/orders?select=items&order=created_at.desc&limit=50"
        orders = _get(orders_url)
        product_count = {}
        for order in orders:
            items = order.get('items', [])
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []
            for item in (items if isinstance(items, list) else []):
                pid = item.get('product_id')
                if pid:
                    product_count[pid] = product_count.get(pid, 0) + item.get('quantity', 1)

        if not product_count:
            result = get_featured_products(limit=limit)
            cache_set(cache_key, result, ttl=300)
            return result

        sorted_ids = sorted(product_count, key=product_count.get, reverse=True)[:limit]
        trending = []
        for pid in sorted_ids:
            p = get_product_by_id(pid)
            if p and p.get('is_active'):
                trending.append(p)

        if len(trending) < limit:
            featured = get_featured_products(limit=limit)
            existing = {p['id'] for p in trending}
            for p in featured:
                if p['id'] not in existing and len(trending) < limit:
                    trending.append(p)

        cache_set(cache_key, trending, ttl=300)
        return trending
    except Exception as e:
        print(f"get_trending_products error: {e}")
        return get_featured_products(limit=limit)

def get_buy_again_products(user_id, limit=8):
    """Products previously ordered by this user"""
    cache_key = f"buyagain:{user_id}:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        import json
        orders_url = f"{SUPABASE_URL}/rest/v1/orders?user_id=eq.{user_id}&select=items&order=created_at.desc&limit=10"
        orders = _get(orders_url)
        seen_ids, seen_set = [], set()
        for order in orders:
            items = order.get('items', [])
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []
            for item in (items if isinstance(items, list) else []):
                pid = item.get('product_id')
                if pid and pid not in seen_set:
                    seen_ids.append(pid)
                    seen_set.add(pid)
                if len(seen_ids) >= limit:
                    break
            if len(seen_ids) >= limit:
                break

        buy_again = []
        for pid in seen_ids[:limit]:
            p = get_product_by_id(pid)
            if p and p.get('is_active'):
                buy_again.append(p)

        cache_set(cache_key, buy_again, ttl=120)
        return buy_again
    except Exception as e:
        print(f"get_buy_again_products error: {e}")
        return []

def create_product(data):
    try:
        res = _session.post(f"{SUPABASE_URL}/rest/v1/products", json=data, timeout=8)
        if res.status_code in [200, 201]:
            cache_clear_prefix("cat:")
            cache_clear_prefix("featured:")
            cache_clear_prefix("new:")
            cache_clear_prefix("deals:")
            return res.json()
        return None
    except Exception as e:
        print(f"create_product error: {e}")
        return None

def update_product(product_id, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}"
        res = _session.patch(url, json=data, timeout=8)
        # Clear cache for this product
        cache_clear_prefix(f"product:{product_id}")
        cache_clear_prefix("cat:")
        cache_clear_prefix("featured:")
        cache_clear_prefix("new:")
        cache_clear_prefix("deals:")
        return True if res.status_code in [200, 201, 204] else None
    except Exception as e:
        print(f"update_product error: {e}")
        return None

def delete_product(product_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}"
        _session.patch(url, json={"is_active": False}, timeout=8)
        cache_clear_prefix(f"product:{product_id}")
        cache_clear_prefix("cat:")
        cache_clear_prefix("featured:")
        return True
    except Exception as e:
        return False

def search_products(query, limit=10):
    try:
        url = f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&name=ilike.*{requests.utils.quote(query)}*&select=id,name,price,discount,image_url&limit={limit}"
        return _get(url)
    except Exception as e:
        return []

def count_products():
    cache_key = "count:products"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        count_headers = {**HEADERS, "Prefer": "count=exact"}
        res = _session.get(f"{SUPABASE_URL}/rest/v1/products?is_active=eq.true&select=id",
                          headers=count_headers, timeout=8)
        count_str = res.headers.get('content-range', '0/0').split('/')[-1]
        count = int(count_str) if count_str.isdigit() else len(res.json())
        cache_set(cache_key, count, ttl=60)
        return count
    except Exception as e:
        return 0

def get_home_data_parallel(user_id=None):
    """
    Fetch ALL homepage data in parallel using threads.
    This reduces homepage load from 8 sequential calls (~3s)
    to 1 parallel batch (~400ms).
    """
    def fetch(key, fn, *args, **kwargs):
        return key, fn(*args, **kwargs)

    tasks = {
        'featured':  (get_featured_products, [], {'limit': 8}),
        'beauty':    (get_products_by_category, ['Beauty & Personal Care'], {'limit': 6}),
        'grocery':   (get_products_by_category, ['Grocery'], {'limit': 6}),
        'snacks':    (get_products_by_category, ['Snacks & Drinks'], {'limit': 6}),
        'deals':     (get_best_deals, [], {'limit': 8}),
        'new':       (get_newly_added, [], {'limit': 8}),
        'trending':  (get_trending_products, [], {'limit': 8}),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            executor.submit(fn, *args, **kwargs): key
            for key, (fn, args, kwargs) in tasks.items()
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                print(f"Parallel fetch error for {key}: {e}")
                results[key] = []

    # Buy again is user-specific, fetch separately
    results['buy_again'] = []
    if user_id:
        results['buy_again'] = get_buy_again_products(user_id, limit=8)

    return results
