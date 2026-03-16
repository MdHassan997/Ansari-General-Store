-- ============================================
-- COUPONS TABLE — Run in Supabase SQL Editor
-- ============================================

CREATE TABLE IF NOT EXISTS public.coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    description TEXT DEFAULT '',
    discount_type TEXT NOT NULL DEFAULT 'percentage',
    -- discount_type options:
    -- 'percentage'    → e.g. 10% off subtotal
    -- 'fixed'         → e.g. ₹50 off subtotal
    -- 'free_delivery' → delivery charge becomes ₹0
    discount_value NUMERIC(10,2) DEFAULT 0,
    max_discount_amount NUMERIC(10,2) DEFAULT NULL,
    min_order_amount NUMERIC(10,2) DEFAULT 0,
    max_uses INTEGER DEFAULT NULL,
    used_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.coupons ENABLE ROW LEVEL SECURITY;

-- Public can read active coupons (for validation)
CREATE POLICY "Anyone can read active coupons"
    ON public.coupons FOR SELECT
    USING (is_active = TRUE);

-- ============================================
-- SAMPLE COUPONS — Ready to use immediately
-- ============================================

INSERT INTO public.coupons (code, description, discount_type, discount_value, min_order_amount, max_uses)
VALUES
    -- Free delivery no matter what
    ('FREEDEL', 'Free delivery on any order', 'free_delivery', 0, 0, NULL),

    -- Free delivery on orders above ₹200
    ('DELIVER200', 'Free delivery on orders above ₹200', 'free_delivery', 0, 200, NULL),

    -- 10% off on any order
    ('SAVE10', '10% off on your order', 'percentage', 10, 0, NULL),

    -- 20% off — max discount ₹100
    ('SAVE20', '20% off (max ₹100 discount)', 'percentage', 20, 0, NULL),

    -- ₹50 flat off on orders above ₹300
    ('FLAT50', '₹50 off on orders above ₹300', 'fixed', 50, 300, NULL),

    -- ₹100 flat off on orders above ₹500
    ('FLAT100', '₹100 off on orders above ₹500', 'fixed', 100, 500, NULL),

    -- Welcome coupon — 15% off, one-time use limit 100
    ('WELCOME15', '15% off for new customers', 'percentage', 15, 0, 100),

    -- Weekend special — 5% off
    ('WEEKEND5', '5% off this weekend', 'percentage', 5, 0, NULL)

ON CONFLICT (code) DO NOTHING;

-- ============================================
-- HOW TO ADD YOUR OWN COUPONS:
-- ============================================
-- Example 1: Free delivery coupon
-- INSERT INTO public.coupons (code, description, discount_type, discount_value, min_order_amount)
-- VALUES ('MYCODE', 'Free delivery', 'free_delivery', 0, 0);

-- Example 2: 25% off coupon with ₹150 max discount
-- INSERT INTO public.coupons (code, description, discount_type, discount_value, max_discount_amount, min_order_amount)
-- VALUES ('SALE25', '25% off sale', 'percentage', 25, 150, 0);

-- Example 3: ₹75 flat off on orders above ₹400
-- INSERT INTO public.coupons (code, description, discount_type, discount_value, min_order_amount)
-- VALUES ('GET75', '₹75 off on ₹400+', 'fixed', 75, 400);

-- Example 4: Limited use coupon (only 50 uses)
-- INSERT INTO public.coupons (code, description, discount_type, discount_value, max_uses)
-- VALUES ('SPECIAL', 'Special offer', 'percentage', 30, 50);
