from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.cart_model import (get_cart_items, add_to_cart, update_cart_quantity,
                                remove_from_cart, clear_cart, get_cart_count,
                                get_wishlist, add_to_wishlist, remove_from_wishlist)

cart_bp = Blueprint('cart', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            if request.is_json:
                return jsonify({'error': 'Login required', 'redirect': url_for('auth.login')}), 401
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated

@cart_bp.route('/cart')
@login_required
def cart():
    user_id = session['user_id']
    items = get_cart_items(user_id)
    
    subtotal = 0
    for item in items:
        product = item.get('products', {}) or {}
        price = float(product.get('price', 0))
        discount = float(product.get('discount', 0))
        discounted_price = price - (price * discount / 100)
        item['discounted_price'] = round(discounted_price, 2)
        item['item_total'] = round(discounted_price * item['quantity'], 2)
        subtotal += item['item_total']
    
    delivery_charge = 40 if subtotal < 500 else 0
    total = subtotal + delivery_charge
    
    return render_template('cart.html',
        items=items,
        subtotal=round(subtotal, 2),
        delivery_charge=delivery_charge,
        total=round(total, 2)
    )

@cart_bp.route('/api/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID required'})
    
    success = add_to_cart(session['user_id'], product_id, quantity)
    count = get_cart_count(session['user_id'])
    return jsonify({'success': success, 'cart_count': count})

@cart_bp.route('/api/cart/update', methods=['POST'])
@login_required
def api_update_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    update_cart_quantity(session['user_id'], product_id, quantity)
    count = get_cart_count(session['user_id'])
    return jsonify({'success': True, 'cart_count': count})

@cart_bp.route('/api/cart/remove', methods=['POST'])
@login_required
def api_remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    remove_from_cart(session['user_id'], product_id)
    count = get_cart_count(session['user_id'])
    return jsonify({'success': True, 'cart_count': count})

@cart_bp.route('/wishlist')
@login_required
def wishlist():
    user_id = session['user_id']
    items = get_wishlist(user_id)
    return render_template('wishlist.html', items=items)

@cart_bp.route('/api/wishlist/add', methods=['POST'])
@login_required
def api_add_to_wishlist():
    data = request.get_json()
    product_id = data.get('product_id')
    success = add_to_wishlist(session['user_id'], product_id)
    return jsonify({'success': success})

@cart_bp.route('/api/wishlist/remove', methods=['POST'])
@login_required
def api_remove_from_wishlist():
    data = request.get_json()
    product_id = data.get('product_id')
    success = remove_from_wishlist(session['user_id'], product_id)
    return jsonify({'success': success})

@cart_bp.route('/api/cart/count')
def api_cart_count():
    if not session.get('user_id'):
        return jsonify({'count': 0})
    count = get_cart_count(session['user_id'])
    return jsonify({'count': count})
