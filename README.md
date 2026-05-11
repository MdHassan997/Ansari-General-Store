# Ansari General Store 🛒

A full-stack e-commerce website I built for my family's physical grocery store in India. The idea was simple — customers kept asking if they could order online, so I decided to build something proper instead of just using WhatsApp.

Built with Python Flask on the backend, Supabase as the database, and Razorpay for payments. No fancy frameworks — just clean HTML, CSS, and vanilla JavaScript on the frontend.

---

## Why I Built This

We've been running a physical store for years. Customers would call up, place orders verbally, and we'd deliver manually with no tracking system. It worked, but barely. I wanted something where:

- Customers can browse and order on their own
- We get proper order notifications with delivery slots
- Payments can happen online (UPI, cards, net banking)
- Someone can pick up from the store if they prefer
- I can manage everything from an admin panel without touching code

So here we are.

---

## What It Does

**For customers:**
- Browse products across 3 main categories — Grocery, Snacks & Drinks, Beauty & Personal Care
- Each category has proper subcategories (Fresh Fruits, Hair Care, Chips & Namkeens, etc.)
- Add to cart, save to wishlist, place orders
- Choose between home delivery or store pickup
- Pick a delivery time slot that works for them
- Pay online via Razorpay (UPI, debit/credit card, net banking, wallets) or cash on delivery
- Track order status — from placed to delivered
- Apply discount coupons (free delivery, percentage off, flat discount)
- See order history with full details

**For the store owner (admin):**
- Add/edit/delete products with an image search tool built in
- Mark products as featured to show on homepage
- Manage all orders and update their status
- Create and manage discount coupons
- See revenue stats and recent orders on a dashboard

---

## Tech Stack

| What | Which |
|---|---|
| Backend | Python Flask |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Authentication |
| Storage | Supabase Storage |
| Payments | Razorpay |
| Frontend | HTML5, CSS3, Vanilla JS |
| Fonts | Google Fonts (Playfair Display + DM Sans) |
| Icons | Font Awesome 6 |
| Hosting ready | Gunicorn + any VPS or Render.com |

---

## Project Structure

```
ansari_general_store/
├── app.py                    # Flask app entry point
├── config.py                 # All config, categories, delivery slots
├── requirements.txt
├── supabase_schema.sql       # Run this first in Supabase SQL editor
├── supabase_coupons.sql      # Creates the coupons table
│
├── routes/
│   ├── auth_routes.py        # Login, signup, profile
│   ├── product_routes.py     # Listing, detail, search API
│   ├── cart_routes.py        # Cart and wishlist AJAX endpoints
│   ├── order_routes.py       # Checkout, Razorpay, coupon validation
│   └── admin_routes.py       # Full admin panel
│
├── models/
│   ├── user_model.py
│   ├── product_model.py      # Includes parallel fetch for homepage speed
│   ├── cart_model.py
│   ├── order_model.py
│   └── coupon_model.py
│
├── utils/
│   ├── supabase_client.py
│   ├── payment_gateway.py    # Razorpay integration using REST API
│   └── cache.py              # Simple in-memory cache for speed
│
├── templates/
│   ├── base.html             # Navbar, footer, flash messages
│   ├── home.html             # Hero slider, categories, product sections
│   ├── products.html         # Listing with sidebar filters
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html         # With coupon system + Razorpay
│   ├── wishlist.html
│   ├── orders.html
│   ├── order_detail.html     # With visual status tracker
│   ├── order_success.html
│   ├── profile.html
│   ├── login.html
│   ├── signup.html
│   └── admin/
│       ├── admin_dashboard.html
│       ├── admin_products.html
│       ├── admin_product_form.html  # Has image search tool built in
│       ├── admin_orders.html
│       └── admin_coupons.html
│
└── static/
    ├── css/style.css         # ~700 lines, custom green theme
    └── js/main.js            # Slider, search suggestions, cart AJAX
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/ansari-general-store.git
cd ansari-general-store
```

### 2. Set up Supabase

- Create a free project at [supabase.com](https://supabase.com)
- Go to SQL Editor and run `supabase_schema.sql` — this creates all tables and loads 31 sample products
- Then run `supabase_coupons.sql` — this creates the coupons table with some default coupons
- Create a storage bucket called `product-images` and set it to public

### 3. Get Razorpay test keys

- Sign up at [razorpay.com](https://razorpay.com)
- Generate test mode API keys from Settings → API Keys

### 4. Configure environment

```bash
cp .env.example .env
```

Fill in your actual values:

```env
FLASK_SECRET_KEY=your-secret-key
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=your-secret
STORE_NAME=Ansari General Store
STORE_ADDRESS=Your Shop Address
STORE_PHONE=+91-XXXXXXXXXX
STORE_EMAIL=your@email.com
CURRENCY=INR
CURRENCY_SYMBOL=₹
```

### 5. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 6. Run

```bash
python app.py
```

Open `http://localhost:5000`

### 7. Make yourself admin

After signing up, go to Supabase SQL Editor and run:

```sql
UPDATE public.users SET is_admin = TRUE WHERE email = 'your@email.com';
```

Log out and back in — you'll see the Admin Panel link.

---

## Testing Payments

Use these Razorpay test credentials in the checkout:

| Field | Value |
|---|---|
| Card Number | `4111 1111 1111 1111` |
| Expiry | Any future date |
| CVV | Any 3 digits |
| UPI ID | `success@razorpay` |
| OTP | `1234` |

---

## Default Coupons (ready to use after running the SQL)

| Code | Type | Benefit |
|---|---|---|
| `FREEDEL` | Free delivery | Works on any order amount |
| `SAVE10` | 10% off | No minimum |
| `FLAT50` | ₹50 off | On orders above ₹300 |
| `FLAT100` | ₹100 off | On orders above ₹500 |
| `WELCOME15` | 15% off | Limited to 100 uses |

---

## Product Categories

**Grocery** — Fresh Fruits, Fresh Vegetables, Atta/Rice/Dal, Oil/Ghee/Masala, Dairy/Bread/Eggs, Cereals & Dry Fruits, Chicken/Fish/Meats, Instant & Frozen Food

**Snacks & Drinks** — Drinks & Juices, Chips & Namkeens, Bakery & Biscuits, Sweets, Chocolates, Ice Creams, Sauces & Spreads, Tea/Coffee/Milk Drinks

**Beauty & Personal Care** — Bath & Body, Baby Care, Hair Care, Beauty Products, Fragrances, Grooming & Hygiene

---

## Deployment

The app is ready to deploy. I use Gunicorn which is already in requirements.txt.

For Render.com:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add all your `.env` variables in the Environment section

---

## A Few Notes

- The Supabase free tier pauses after 7 days of inactivity. Just resume it from the dashboard — takes 30 seconds. Upgrade to Pro ($25/month) when you have actual paying customers.
- The Razorpay test mode works immediately without KYC. Switch to live mode and complete KYC when you're ready to accept real money.
- The image search tool in the admin panel uses a curated database of Wikimedia Commons images — all copyright free. For branded products, it searches Open Food Facts.
- Homepage data is fetched in parallel using Python threads so the page doesn't take forever to load.

---

## License

MIT — use it however you like.
