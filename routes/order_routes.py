import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.cart_model import get_cart_items, clear_cart, get_cart_count
from models.order_model import create_order, get_user_orders, get_order_by_id, update_payment_status
from models.user_model import get_user_by_id
from models.coupon_model import validate_coupon, increment_coupon_usage
from utils.payment_gateway import create_razorpay_order, verify_razorpay_payment, get_payment_config
from config import Config

order_bp = Blueprint('order', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated

def calculate_cart_totals(items):
    subtotal = 0
    for item in items:
        product = item.get('products', {}) or {}
        price = float(product.get('price', 0))
        discount = float(product.get('discount', 0))
        discounted_price = price - (price * discount / 100)
        item['discounted_price'] = round(discounted_price, 2)
        item['item_total'] = round(discounted_price * item['quantity'], 2)
        item['savings'] = round((price - discounted_price) * item['quantity'], 2)
        subtotal += item['item_total']
    return round(subtotal, 2)

@order_bp.route('/checkout')
@login_required
def checkout():
    user_id = session['user_id']
    items = get_cart_items(user_id)
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.cart'))

    subtotal = calculate_cart_totals(items)
    total_savings = sum(item.get('savings', 0) for item in items)
    delivery_charge = 40 if subtotal < 500 else 0
    total = subtotal + delivery_charge
    user = get_user_by_id(user_id)
    payment_config = get_payment_config()

    return render_template('checkout.html',
        items=items,
        subtotal=round(subtotal, 2),
        total_savings=round(total_savings, 2),
        delivery_charge=delivery_charge,
        total=round(total, 2),
        user=user,
        delivery_slots=Config.DELIVERY_SLOTS,
        payment_config=payment_config
    )

@order_bp.route('/api/coupon/validate', methods=['POST'])
@login_required
def validate_coupon_route():
    data = request.get_json()
    code = data.get('code', '').strip()
    subtotal = float(data.get('subtotal', 0))
    if not code:
        return jsonify({'valid': False, 'error': 'Please enter a coupon code'})
    result = validate_coupon(code, subtotal, session['user_id'])
    return jsonify(result)

@order_bp.route('/order/create', methods=['POST'])
@login_required
def create_order_route():
    user_id = session['user_id']
    items = get_cart_items(user_id)
    if not items:
        return jsonify({'success': False, 'error': 'Cart is empty'})

    subtotal = 0
    order_items = []
    for item in items:
        product = item.get('products', {}) or {}
        price = float(product.get('price', 0))
        discount = float(product.get('discount', 0))
        discounted_price = price - (price * discount / 100)
        item_total = round(discounted_price * item['quantity'], 2)
        subtotal += item_total
        order_items.append({
            'product_id': item['product_id'],
            'name': product.get('name', ''),
            'image_url': product.get('image_url', ''),
            'price': price,
            'discount': discount,
            'discounted_price': round(discounted_price, 2),
            'quantity': item['quantity'],
            'item_total': item_total
        })

    subtotal = round(subtotal, 2)
    delivery_charge = 40 if subtotal < 500 else 0
    coupon_code = request.form.get('coupon_code', '').strip()
    coupon_discount = 0
    coupon_description = ''

    if coupon_code:
        coupon_result = validate_coupon(coupon_code, subtotal, user_id)
        if coupon_result.get('valid'):
            coupon_discount = coupon_result.get('discount_amount', 0)
            delivery_charge = coupon_result.get('new_delivery_charge', delivery_charge)
            coupon_description = coupon_result.get('description', '')
        else:
            return jsonify({'success': False, 'error': coupon_result.get('error', 'Invalid coupon')})

    total = round(max(subtotal + delivery_charge - coupon_discount, 0), 2)
    delivery_type = request.form.get('delivery_type', 'delivery')
    delivery_address = request.form.get('delivery_address', '')
    delivery_time_slot = request.form.get('delivery_time_slot', '')
    payment_method = request.form.get('payment_method', 'online')
    notes = request.form.get('notes', '')

    if delivery_type == 'delivery' and not delivery_address:
        return jsonify({'success': False, 'error': 'Delivery address required'})

    if coupon_code and coupon_description:
        notes = f"Coupon: {coupon_code} ({coupon_description}). {notes}".strip()

    order = create_order(
        user_id=user_id, items=order_items, total_price=total,
        delivery_type=delivery_type, delivery_address=delivery_address,
        delivery_time_slot=delivery_time_slot, payment_method=payment_method, notes=notes
    )

    if not order:
        return jsonify({'success': False, 'error': 'Failed to create order'})

    if coupon_code:
        increment_coupon_usage(coupon_code)

    if payment_method == 'online':
        rp_result = create_razorpay_order(total, order['id'])
        if rp_result['success']:
            return jsonify({
                'success': True,
                'order_id': order['id'],
                'razorpay_order_id': rp_result['order']['id'],
                'amount': int(total * 100),
                'key_id': Config.RAZORPAY_KEY_ID
            })
        else:
            return jsonify({'success': False, 'error': 'Payment gateway error'})
    else:
        clear_cart(user_id)
        return jsonify({'success': True, 'order_id': order['id'],
                       'redirect': url_for('order.order_success', order_id=order['id'])})

@order_bp.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    data = request.get_json()
    order_id = data.get('order_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    is_valid = verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    if is_valid:
        update_payment_status(order_id, 'paid', razorpay_payment_id, razorpay_order_id)
        clear_cart(session['user_id'])
        return jsonify({'success': True, 'redirect': url_for('order.order_success', order_id=order_id)})
    else:
        update_payment_status(order_id, 'failed')
        return jsonify({'success': False, 'error': 'Payment verification failed'})

@order_bp.route('/order/success/<order_id>')
@login_required
def order_success(order_id):
    order = get_order_by_id(order_id)
    if not order or order['user_id'] != session['user_id']:
        return redirect(url_for('main.home'))
    return render_template('order_success.html', order=order)

@order_bp.route('/orders')
@login_required
def my_orders():
    orders = get_user_orders(session['user_id'])
    return render_template('orders.html', orders=orders)

@order_bp.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    order = get_order_by_id(order_id)
    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'error')
        return redirect(url_for('order.my_orders'))
    return render_template('order_detail.html', order=order)
