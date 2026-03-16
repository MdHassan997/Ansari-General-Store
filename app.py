from flask import Flask, render_template, session, Blueprint
from config import Config
from models.product_model import (get_featured_products, get_products_by_category,
                                   get_best_deals, get_newly_added,
                                   get_trending_products, get_buy_again_products)
from models.cart_model import get_cart_count

# ── App Init ──
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# ── Register Blueprints ──
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)

# ── Main Blueprint (home) ──
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    featured        = get_featured_products(limit=8)
    beauty_products = get_products_by_category('Beauty & Personal Care', limit=6)
    grocery_products= get_products_by_category('Grocery', limit=6)
    snack_products  = get_products_by_category('Snacks & Drinks', limit=6)
    best_deals      = get_best_deals(limit=8)
    newly_added     = get_newly_added(limit=8)
    trending        = get_trending_products(limit=8)

    # Buy Again only for logged-in users
    buy_again = []
    if session.get('user_id'):
        buy_again = get_buy_again_products(session['user_id'], limit=8)

    return render_template('home.html',
        featured_products=featured,
        beauty_products=beauty_products,
        grocery_products=grocery_products,
        snack_products=snack_products,
        best_deals=best_deals,
        newly_added=newly_added,
        trending_products=trending,
        buy_again_products=buy_again,
    )

app.register_blueprint(main_bp)

# ── Context Processor ──
@app.context_processor
def inject_globals():
    cart_count = 0
    if session.get('user_id'):
        try:
            cart_count = get_cart_count(session['user_id'])
        except Exception:
            cart_count = 0
    return {
        'cart_count': cart_count,
        'store_name': Config.STORE_NAME,
        'store_phone': Config.STORE_PHONE,
        'store_email': Config.STORE_EMAIL,
        'store_address': Config.STORE_ADDRESS,
        'currency_symbol': Config.CURRENCY_SYMBOL,
        'categories': Config.CATEGORIES,
        'category_icons': Config.CATEGORY_ICONS,
    }

# ── Error Handlers ──
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
