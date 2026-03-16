-- ============================================
-- ANSARI GENERAL STORE — Supabase SQL Schema
-- Run this in your Supabase SQL editor
-- ============================================

-- USERS TABLE (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT '',
    email TEXT UNIQUE NOT NULL,
    phone TEXT DEFAULT '',
    address TEXT DEFAULT '',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT DEFAULT '',
    price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    discount NUMERIC(5, 2) DEFAULT 0,
    description TEXT DEFAULT '',
    image_url TEXT DEFAULT '',
    stock INTEGER DEFAULT 0,
    rating NUMERIC(3, 1) DEFAULT 4.0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ORDERS TABLE
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    items JSONB DEFAULT '[]',
    total_price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    payment_status TEXT DEFAULT 'pending',
    payment_method TEXT DEFAULT 'online',
    razorpay_order_id TEXT DEFAULT '',
    razorpay_payment_id TEXT DEFAULT '',
    delivery_type TEXT DEFAULT 'delivery',
    delivery_address TEXT DEFAULT '',
    delivery_time_slot TEXT DEFAULT '',
    order_status TEXT DEFAULT 'Order Placed',
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CART TABLE
CREATE TABLE IF NOT EXISTS public.cart (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- WISHLIST TABLE
CREATE TABLE IF NOT EXISTS public.wishlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- INDEXES for performance
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON public.products(subcategory);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_is_featured ON public.products(is_featured);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON public.orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cart_user_id ON public.cart(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_user_id ON public.wishlist(user_id);

-- ROW LEVEL SECURITY (RLS)
ALTER TABLE public.users    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cart     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wishlist ENABLE ROW LEVEL SECURITY;

-- POLICIES: users
CREATE POLICY "Users can read own profile"
    ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE USING (auth.uid() = id);

-- POLICIES: products (public read, admin write)
CREATE POLICY "Anyone can view active products"
    ON public.products FOR SELECT USING (is_active = TRUE);

-- POLICIES: cart (own rows only)
CREATE POLICY "Users manage own cart"
    ON public.cart FOR ALL USING (auth.uid() = user_id);

-- POLICIES: wishlist (own rows only)
CREATE POLICY "Users manage own wishlist"
    ON public.wishlist FOR ALL USING (auth.uid() = user_id);

-- POLICIES: orders (own rows)
CREATE POLICY "Users view own orders"
    ON public.orders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users create own orders"
    ON public.orders FOR INSERT WITH CHECK (auth.uid() = user_id);

-- STORAGE BUCKET for product images
-- Run this in Supabase Dashboard > Storage > Create Bucket
-- Name: product-images
-- Public: Yes

-- INSERT SAMPLE PRODUCTS
INSERT INTO public.products (name, category, subcategory, price, discount, description, stock, rating, is_featured)
VALUES
-- Grocery
('Organic Basmati Rice 5kg', 'Grocery', 'Atta, Rice & Dal', 399.00, 10, 'Premium long-grain aromatic basmati rice, sourced from the finest farms.', 50, 4.5, TRUE),
('Toor Dal 1kg', 'Grocery', 'Atta, Rice & Dal', 140.00, 5, 'High quality toor dal, protein rich and perfect for everyday dal recipes.', 80, 4.3, FALSE),
('Aashirvaad Atta 10kg', 'Grocery', 'Atta, Rice & Dal', 420.00, 8, 'Whole wheat flour for soft, nutritious rotis.', 40, 4.7, TRUE),
('Fortune Sunflower Oil 5L', 'Grocery', 'Oil, Ghee & Masala', 680.00, 5, 'Light refined sunflower oil for healthy cooking.', 30, 4.2, FALSE),
('Amul Ghee 1L', 'Grocery', 'Oil, Ghee & Masala', 580.00, 0, 'Pure cow ghee, rich and aromatic.', 25, 4.8, TRUE),
('MDH Garam Masala 100g', 'Grocery', 'Oil, Ghee & Masala', 85.00, 0, 'Authentic blend of whole spices for rich flavour.', 100, 4.6, FALSE),
('Amul Full Cream Milk 1L', 'Grocery', 'Dairy, Bread & Eggs', 68.00, 0, 'Fresh pasteurized full cream milk.', 60, 4.5, FALSE),
('Britannia Brown Bread', 'Grocery', 'Dairy, Bread & Eggs', 42.00, 0, 'Wholesome brown bread, freshly baked.', 40, 4.3, FALSE),
('Farm Fresh Eggs (Dozen)', 'Grocery', 'Dairy, Bread & Eggs', 90.00, 0, 'Farm fresh white eggs, dozen pack.', 70, 4.6, TRUE),
('Red Apple 1kg', 'Grocery', 'Fresh Fruits', 120.00, 10, 'Fresh, juicy Himachali red apples.', 45, 4.7, TRUE),
('Banana (Dozen)', 'Grocery', 'Fresh Fruits', 60.00, 0, 'Sweet ripe bananas, rich in potassium.', 50, 4.5, FALSE),
('Tomato 1kg', 'Grocery', 'Fresh Vegetables', 40.00, 0, 'Fresh ripe tomatoes, locally sourced.', 100, 4.2, FALSE),
('Onion 1kg', 'Grocery', 'Fresh Vegetables', 35.00, 0, 'Fresh red onions, essential for every kitchen.', 150, 4.1, FALSE),
('Spinach 500g', 'Grocery', 'Fresh Vegetables', 28.00, 0, 'Fresh green spinach leaves.', 60, 4.4, FALSE),
('Chicken Breast 500g', 'Grocery', 'Chicken, Fish & Meats', 220.00, 5, 'Fresh boneless chicken breast, cleaned and ready to cook.', 30, 4.6, TRUE),

-- Snacks & Drinks
('Lays Classic Salted 26g', 'Snacks & Drinks', 'Chips & Namkeens', 20.00, 0, 'Crispy salted potato chips.', 200, 4.3, FALSE),
('Kurkure Masala Munch', 'Snacks & Drinks', 'Chips & Namkeens', 20.00, 0, 'Crunchy corn puffs with masala flavour.', 180, 4.4, FALSE),
('Coca-Cola 750ml', 'Snacks & Drinks', 'Drinks & Juices', 45.00, 0, 'Chilled refreshing cola drink.', 80, 4.2, FALSE),
('Tropicana Orange Juice 1L', 'Snacks & Drinks', 'Drinks & Juices', 130.00, 5, '100% real orange juice, no added sugar.', 50, 4.5, TRUE),
('Parle-G Biscuits 200g', 'Snacks & Drinks', 'Bakery & Biscuits', 30.00, 0, 'Iconic glucose biscuit loved by all.', 250, 4.7, FALSE),
('Dairy Milk Silk 60g', 'Snacks & Drinks', 'Chocolates', 100.00, 10, 'Smooth and creamy milk chocolate bar.', 100, 4.8, TRUE),
('Kwality Walls Cornetto', 'Snacks & Drinks', 'Ice Creams', 50.00, 0, 'Crispy cone with creamy vanilla ice cream.', 40, 4.6, FALSE),
('Tata Tea Gold 500g', 'Snacks & Drinks', 'Tea, Coffee & Milk Drinks', 240.00, 5, 'Rich and aromatic loose leaf tea.', 60, 4.5, TRUE),
('Maggi Hot Sweet Sauce', 'Snacks & Drinks', 'Sauces & Spreads', 85.00, 0, 'Classic Maggi tomato chilli sauce.', 90, 4.4, FALSE),
('Haldiram Rasgulla 1kg', 'Snacks & Drinks', 'Sweets', 180.00, 0, 'Soft and spongy Bengali rasgulla.', 35, 4.6, FALSE),

-- Beauty & Personal Care
('Dove Body Wash 200ml', 'Beauty & Personal Care', 'Bath & Body', 199.00, 10, 'Moisturising body wash with ¼ moisturising cream.', 50, 4.6, TRUE),
('Himalaya Baby Lotion 400ml', 'Beauty & Personal Care', 'Baby Care', 220.00, 5, 'Gentle baby lotion with natural herbs.', 40, 4.7, FALSE),
('Pantene Anti-Hairfall Shampoo 340ml', 'Beauty & Personal Care', 'Hair Care', 280.00, 8, 'Pro-Vitamin formula to reduce hair fall.', 45, 4.5, TRUE),
('Lakme Lip Colour', 'Beauty & Personal Care', 'Beauty Products', 250.00, 0, 'Long-lasting lip colour in classic red.', 30, 4.4, FALSE),
('Fogg Black Deo 150ml', 'Beauty & Personal Care', 'Fragrances', 200.00, 10, 'Long-lasting deodorant bodyspray for men.', 60, 4.6, TRUE),
('Gillette Mach3 Razor', 'Beauty & Personal Care', 'Grooming & Hygiene', 350.00, 0, 'Triple blade razor for a smooth shave.', 40, 4.7, FALSE)
ON CONFLICT DO NOTHING;

-- ============================================
-- MAKE YOURSELF ADMIN:
-- After signing up with your email, run this:
-- UPDATE public.users SET is_admin = TRUE WHERE email = 'your-email@example.com';
-- ============================================
