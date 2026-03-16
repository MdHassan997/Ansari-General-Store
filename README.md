# 🛒 Ansari General Store — Full Stack E-Commerce Website

A production-ready grocery store e-commerce website built with **Flask + Supabase + Razorpay**.

---

## 📁 Project Structure

```
ansari_general_store/
├── app.py                      # Main Flask application
├── config.py                   # App configuration & settings
├── requirements.txt            # Python dependencies
├── supabase_schema.sql         # Database schema (run in Supabase)
├── .env.example                # Environment variables template
│
├── routes/
│   ├── auth_routes.py          # Login, signup, profile
│   ├── product_routes.py       # Product listing & detail
│   ├── cart_routes.py          # Cart & wishlist APIs
│   ├── order_routes.py         # Checkout, payment, orders
│   └── admin_routes.py         # Admin panel
│
├── models/
│   ├── user_model.py           # User DB operations
│   ├── product_model.py        # Product DB operations
│   ├── cart_model.py           # Cart & wishlist DB ops
│   └── order_model.py          # Order DB operations
│
├── utils/
│   ├── supabase_client.py      # Supabase client init
│   └── payment_gateway.py      # Razorpay integration
│
├── templates/
│   ├── base.html               # Base layout (navbar, footer)
│   ├── home.html               # Homepage with slider & products
│   ├── products.html           # Product listing page
│   ├── product_detail.html     # Single product page
│   ├── cart.html               # Shopping cart
│   ├── checkout.html           # Checkout + Razorpay payment
│   ├── wishlist.html           # Wishlist page
│   ├── login.html              # Login page
│   ├── signup.html             # Sign up page
│   ├── forgot_password.html    # Password reset
│   ├── profile.html            # User profile
│   ├── orders.html             # Order history
│   ├── order_detail.html       # Single order detail + tracker
│   ├── order_success.html      # Order confirmation page
│   ├── _product_card.html      # Reusable product card partial
│   ├── 404.html                # Not found page
│   ├── 500.html                # Server error page
│   └── admin/
│       ├── admin_dashboard.html
│       ├── admin_products.html
│       ├── admin_product_form.html
│       └── admin_orders.html
│
└── static/
    ├── css/style.css           # Complete stylesheet
    └── js/main.js              # All JavaScript
```

---

## 🚀 Setup & Installation

### Step 1 — Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a free project
2. In **SQL Editor**, paste and run the contents of `supabase_schema.sql`
3. Go to **Storage** → Create a bucket named `product-images` (set to Public)
4. Copy your **Project URL** and **API Keys** from Settings → API

### Step 2 — Get Razorpay Keys
1. Sign up at [razorpay.com](https://razorpay.com)
2. Go to Dashboard → Settings → API Keys
3. Generate Test API keys (use Test mode for development)

### Step 3 — Configure Environment
```bash
cp .env.example .env
# Edit .env and fill in your actual values
```

### Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Run the Application
```bash
python app.py
```
Visit `http://localhost:5000`

---

## 👑 Making Yourself Admin

After signing up on the website, run this SQL in Supabase:
```sql
UPDATE public.users SET is_admin = TRUE WHERE email = 'your-email@example.com';
```
Then log out and log back in. You'll see the **Admin Panel** link.

---

## 🛡️ Features

### Customer Features
- ✅ User registration & login (Supabase Auth)
- ✅ Browse products by category & subcategory
- ✅ Search with live suggestions
- ✅ Product detail page with quantity selector
- ✅ Shopping cart with quantity update
- ✅ Wishlist (save favourites)
- ✅ Checkout with Home Delivery or Store Pickup
- ✅ Delivery time slot selection
- ✅ Razorpay payment (UPI, Card, Net Banking, Wallet)
- ✅ Order confirmation & tracking
- ✅ Order history

### Admin Features
- ✅ Dashboard with stats
- ✅ Add/Edit/Delete products
- ✅ Upload product images to Supabase Storage
- ✅ Manage all orders
- ✅ Update order status

---

## 💳 Payment Flow (Razorpay)

1. User fills checkout form
2. Clicks "Place Order" → Flask creates order in DB
3. Flask calls Razorpay API → gets `razorpay_order_id`
4. Razorpay Checkout opens in browser
5. User pays via UPI/Card/Wallet
6. Flask verifies signature → marks order as paid
7. Cart is cleared → redirects to success page

---

## 🗃️ Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Customer profiles (extends Supabase auth) |
| `products` | Product catalogue |
| `cart` | Per-user cart items |
| `wishlist` | Per-user saved items |
| `orders` | All placed orders with items JSON |

---

## 🌐 Deployment (Render / Railway)

1. Push code to GitHub
2. Connect repo to [render.com](https://render.com)
3. Set all environment variables from `.env.example`
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`

---

## 📞 Store Info (Edit in .env)
- **Store Name**: Ansari General Store
- **Phone**: Update `STORE_PHONE` in `.env`
- **Email**: Update `STORE_EMAIL` in `.env`
- **Address**: Update `STORE_ADDRESS` in `.env`

## grocerieshas231@
