from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from models.product_model import (get_all_products, get_product_by_id,
                                   create_product, update_product, delete_product, count_products)
from models.order_model import get_all_orders, update_order_status, count_orders, get_revenue_stats
from models.coupon_model import get_all_coupons, create_coupon, update_coupon, delete_coupon
from config import Config
import uuid
import requests

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

SUPABASE_URL = Config.SUPABASE_URL
SERVICE_KEY = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY
STORAGE_HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
}

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.url))
        if not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated

def upload_image_to_supabase(file):
    try:
        file_bytes = file.read()
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        file_name = f"{uuid.uuid4()}.{file_ext}"
        content_type = file.content_type or 'image/jpeg'
        upload_url = f"{SUPABASE_URL}/storage/v1/object/product-images/{file_name}"
        headers = {**STORAGE_HEADERS, "Content-Type": content_type, "x-upsert": "true"}
        res = requests.post(upload_url, data=file_bytes, headers=headers)
        if res.status_code in [200, 201]:
            return f"{SUPABASE_URL}/storage/v1/object/public/product-images/{file_name}"
        print(f"Image upload failed: {res.text}")
        return None
    except Exception as e:
        print(f"Image upload error: {e}")
        return None

# ── DASHBOARD ─────────────────────────────────────────────────
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_products = count_products()
    total_orders = count_orders()
    revenue = get_revenue_stats()
    recent_orders = get_all_orders(page=1, per_page=5)
    return render_template('admin/admin_dashboard.html',
        total_products=total_products,
        total_orders=total_orders,
        revenue=revenue,
        recent_orders=recent_orders
    )

# ── PRODUCTS ──────────────────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def products():
    page = int(request.args.get('page', 1))
    category = request.args.get('category', '')
    search = request.args.get('q', '')
    items = get_all_products(
        category=category or None,
        search=search or None,
        page=page,
        per_page=50
    )
    return render_template('admin/admin_products.html',
        products=items, page=page,
        categories=Config.CATEGORIES,
        selected_category=category,
        search=search
    )

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '')
        subcategory = request.form.get('subcategory', '')
        price = request.form.get('price', 0)
        discount = request.form.get('discount', 0)
        description = request.form.get('description', '').strip()
        stock = request.form.get('stock', 0)
        is_featured = 'is_featured' in request.form
        image_url = request.form.get('image_url', '').strip()

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                uploaded_url = upload_image_to_supabase(file)
                if uploaded_url:
                    image_url = uploaded_url
                else:
                    flash('Image upload failed. Using URL instead.', 'warning')

        if not name or not category or not price:
            flash('Name, category and price are required.', 'error')
        else:
            data = {
                'name': name, 'category': category, 'subcategory': subcategory,
                'price': float(price), 'discount': float(discount),
                'description': description, 'stock': int(stock),
                'image_url': image_url, 'is_featured': is_featured,
                'is_active': True, 'rating': 4.0
            }
            result = create_product(data)
            if result:
                flash('Product added successfully!', 'success')
                return redirect(url_for('admin.products'))
            else:
                flash('Failed to add product.', 'error')

    return render_template('admin/admin_product_form.html',
        categories=Config.CATEGORIES, product=None, action='Add')

@admin_bp.route('/products/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin.products'))

    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'category': request.form.get('category', ''),
            'subcategory': request.form.get('subcategory', ''),
            'price': float(request.form.get('price', 0)),
            'discount': float(request.form.get('discount', 0)),
            'description': request.form.get('description', '').strip(),
            'stock': int(request.form.get('stock', 0)),
            'is_featured': 'is_featured' in request.form,
        }
        image_url = request.form.get('image_url', '').strip()
        if image_url:
            data['image_url'] = image_url

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                uploaded_url = upload_image_to_supabase(file)
                if uploaded_url:
                    data['image_url'] = uploaded_url
                else:
                    flash('Image upload failed.', 'warning')

        update_product(product_id, data)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/admin_product_form.html',
        categories=Config.CATEGORIES, product=product, action='Edit')

@admin_bp.route('/products/delete/<product_id>', methods=['POST'])
@admin_required
def delete_product_route(product_id):
    delete_product(product_id)
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin.products'))

# ── ORDERS ────────────────────────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def orders():
    page = int(request.args.get('page', 1))
    all_orders = get_all_orders(page=page, per_page=20)
    return render_template('admin/admin_orders.html',
        orders=all_orders, page=page,
        statuses=Config.ORDER_STATUSES
    )

@admin_bp.route('/orders/update-status', methods=['POST'])
@admin_required
def update_order_status_route():
    data = request.get_json()
    order_id = data.get('order_id')
    status = data.get('status')
    if order_id and status:
        update_order_status(order_id, status)
        return jsonify({'success': True})
    return jsonify({'success': False})

# ── COUPONS ───────────────────────────────────────────────────
@admin_bp.route('/coupons')
@admin_required
def coupons():
    all_coupons = get_all_coupons()
    return render_template('admin/admin_coupons.html', coupons=all_coupons)

@admin_bp.route('/coupons/add', methods=['POST'])
@admin_required
def add_coupon():
    data = {
        'code': request.form.get('code', '').strip().upper(),
        'description': request.form.get('description', '').strip(),
        'discount_type': request.form.get('discount_type', 'percentage'),
        'discount_value': float(request.form.get('discount_value', 0)),
        'min_order_amount': float(request.form.get('min_order_amount', 0)),
        'is_active': True,
        'used_count': 0
    }
    max_uses = request.form.get('max_uses', '').strip()
    if max_uses:
        data['max_uses'] = int(max_uses)
    max_discount = request.form.get('max_discount_amount', '').strip()
    if max_discount:
        data['max_discount_amount'] = float(max_discount)
    expires_at = request.form.get('expires_at', '').strip()
    if expires_at:
        data['expires_at'] = expires_at

    if not data['code']:
        flash('Coupon code is required.', 'error')
    else:
        result = create_coupon(data)
        if result:
            flash(f'Coupon {data["code"]} created successfully!', 'success')
        else:
            flash('Failed to create coupon. Code may already exist.', 'error')
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/coupons/toggle/<coupon_id>', methods=['POST'])
@admin_required
def toggle_coupon(coupon_id):
    data = request.get_json()
    is_active = data.get('is_active', True)
    update_coupon(coupon_id, {'is_active': is_active})
    return jsonify({'success': True})

@admin_bp.route('/coupons/delete/<coupon_id>', methods=['POST'])
@admin_required
def delete_coupon_route(coupon_id):
    delete_coupon(coupon_id)
    flash('Coupon deleted.', 'success')
    return redirect(url_for('admin.coupons'))
