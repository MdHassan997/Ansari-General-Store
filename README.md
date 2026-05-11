# Ansari General Store 🛒

A full-stack e-commerce website I built for my family's physical grocery store in India. Customers kept asking if they could order online, so I decided to build something proper instead of just using WhatsApp.

Built with Python Flask on the backend, Supabase as the database, and Razorpay for payments. No fancy frameworks — just clean HTML, CSS, and vanilla JavaScript on the frontend.

---

## Why I Built This

We've been running a physical store for years. Customers would call up, place orders verbally, and we'd deliver manually with no real tracking. It worked, but barely. I wanted something where:

- Customers can browse and order on their own
- We get proper order notifications with delivery time slots
- Payments can happen online — UPI, cards, net banking
- People can also choose to pick up from the store
- I can manage everything from an admin panel without touching code

---

## What It Does

**For customers:**
- Browse products across 3 main categories — Grocery, Snacks & Drinks, Beauty & Personal Care
- Each category has proper subcategories (Fresh Fruits, Hair Care, Chips & Namkeens, etc.)
- Add to cart, save to wishlist, place orders
- Choose between home delivery or store pickup
- Pick a delivery time slot that works for them
- Pay online via Razorpay (UPI, debit/credit card, net banking, wallets) or cash on delivery
- Track order status from placed to delivered
- Apply discount coupons — free delivery, percentage off, flat discount
- Full order history with details

**For the store owner (admin):**
- Add, edit, delete products with an image search tool built in
- Mark products as featured to show on homepage
- Manage all orders and update their status
- Create and manage discount coupons
- Dashboard with revenue stats and recent orders

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

---

## Product Categories

**Grocery** — Fresh Fruits, Fresh Vegetables, Atta/Rice/Dal, Oil/Ghee/Masala, Dairy/Bread/Eggs, Cereals & Dry Fruits, Chicken/Fish/Meats, Instant & Frozen Food

**Snacks & Drinks** — Drinks & Juices, Chips & Namkeens, Bakery & Biscuits, Sweets, Chocolates, Ice Creams, Sauces & Spreads, Tea/Coffee/Milk Drinks

**Beauty & Personal Care** — Bath & Body, Baby Care, Hair Care, Beauty Products, Fragrances, Grooming & Hygiene

---

## A Few Notes

- Homepage data is fetched in parallel using Python threads so the page loads fast instead of making 8 sequential API calls.
- The admin panel has a built-in image search tool using a curated Wikimedia Commons database — all copyright free.
- Coupon system supports free delivery, percentage discounts, and flat amount discounts with minimum order requirements.
- The order detail page has a visual step-by-step status tracker.

---

## License

This is a private project for personal and business use. Not open for public use, redistribution, or modification.
