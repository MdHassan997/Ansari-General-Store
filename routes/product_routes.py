from flask import Blueprint, render_template, request, jsonify, session
from models.product_model import (get_all_products, get_product_by_id,
                                    get_featured_products, search_products, count_products)
from config import Config

product_bp = Blueprint('product', __name__)

@product_bp.route('/products')
def products():
    category = request.args.get('category', '')
    subcategory = request.args.get('subcategory', '')
    search = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = 12
    
    items = get_all_products(
        category=category or None,
        subcategory=subcategory or None,
        search=search or None,
        page=page,
        per_page=per_page
    )
    
    total = count_products()
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('products.html',
        products=items,
        category=category,
        subcategory=subcategory,
        search=search,
        page=page,
        total_pages=total_pages,
        categories=Config.CATEGORIES
    )

@product_bp.route('/product/<product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return render_template('404.html'), 404
    
    related = get_all_products(category=product.get('category'), per_page=4)
    related = [p for p in related if p['id'] != product_id][:4]
    
    return render_template('product_detail.html', product=product, related=related)

@product_bp.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    results = search_products(q, limit=8)
    return jsonify(results)
