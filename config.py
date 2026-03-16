import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'ansari-store-secret-2024')
    SESSION_TYPE = 'filesystem'

    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')

    # Razorpay
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

    # Stripe
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

    # Store Info
    STORE_NAME = os.getenv('STORE_NAME', 'Ansari General Store')
    STORE_ADDRESS = os.getenv('STORE_ADDRESS', '123 Main Street, Your City')
    STORE_PHONE = os.getenv('STORE_PHONE', '+91-XXXXXXXXXX')
    STORE_EMAIL = os.getenv('STORE_EMAIL', 'contact@ansarigeneralstore.com')
    CURRENCY = os.getenv('CURRENCY', 'INR')
    CURRENCY_SYMBOL = os.getenv('CURRENCY_SYMBOL', '₹')

    # Delivery slots
    DELIVERY_SLOTS = [
        '9:00 AM – 11:00 AM',
        '11:00 AM – 1:00 PM',
        '1:00 PM – 3:00 PM',
        '3:00 PM – 6:00 PM',
        '6:00 PM – 9:00 PM',
    ]

    # Categories
    CATEGORIES = {
        'Beauty & Personal Care': [
            'Bath & Body', 'Baby Care', 'Hair Care',
            'Beauty Products', 'Fragrances', 'Grooming & Hygiene'
        ],
        'Grocery': [
            'Fresh Fruits', 'Fresh Vegetables', 'Atta, Rice & Dal',
            'Oil, Ghee & Masala', 'Dairy, Bread & Eggs',
            'Cereals & Dry Fruits', 'Chicken, Fish & Meats',
            'Instant & Frozen Food'
        ],
        'Snacks & Drinks': [
            'Drinks & Juices', 'Chips & Namkeens', 'Bakery & Biscuits',
            'Sweets', 'Chocolates', 'Ice Creams',
            'Sauces & Spreads', 'Tea, Coffee & Milk Drinks'
        ]
    }

    CATEGORY_ICONS = {
        'Beauty & Personal Care': '💄',
        'Grocery': '🛒',
        'Snacks & Drinks': '🍿'
    }

    ORDER_STATUSES = [
        'Order Placed',
        'Payment Confirmed',
        'Preparing Order',
        'Out for Delivery',
        'Delivered',
        'Ready for Pickup',
        'Cancelled'
    ]
