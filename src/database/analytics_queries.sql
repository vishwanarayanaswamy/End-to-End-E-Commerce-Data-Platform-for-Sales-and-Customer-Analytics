-- Business Intelligence & Data Warehouse Analytical Query Suite
-- Capstone Project: End-to-End E-Commerce Data Platform
-- Author: Koushik Raj Singh

-- ==========================================
-- 1. EXECUTIVE SALES OVERVIEW
-- Target: General transaction counts, revenue, and AOV (Average Order Value)
-- ==========================================
SELECT
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity_ordered) AS total_units_sold,
    SUM(f.total_sale_amount) AS gross_revenue,
    SUM(f.discount_amount) AS total_discounts_given,
    SUM(f.total_sale_amount - f.discount_amount) AS net_revenue,
    ROUND(AVG(f.total_sale_amount), 2) AS average_order_value_aov
FROM fact_sales f;

-- ==========================================
-- 2. PRODUCT CATEGORY & BRAND PERFORMANCE
-- Target: Revenue split by category and brands to locate top-tier items
-- ==========================================
SELECT
    p.category,
    p.brand,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity_ordered) AS units_sold,
    SUM(f.total_sale_amount) AS total_revenue,
    ROUND(SUM(f.total_sale_amount) / SUM(SUM(f.total_sale_amount)) OVER () * 100, 2) AS revenue_percentage
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.category, p.brand
ORDER BY total_revenue DESC;

-- ==========================================
-- 3. GEOGRAPHIC PERFORMANCE ANALYSIS
-- Target: Sales volume and active buyer count by country and regional zone
-- ==========================================
SELECT
    c.country,
    c.region,
    COUNT(DISTINCT f.customer_id) AS active_customers,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity_ordered) AS units_sold,
    SUM(f.total_sale_amount) AS total_revenue
FROM fact_sales f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.country, c.region
ORDER BY total_revenue DESC;

-- ==========================================
-- 4. CUSTOMER COHORT RETENTION ANALYSIS
-- Target: Groups customers by first purchase month and tracks monthly repeat purchases
-- ==========================================
WITH customer_cohorts AS (
    -- Step 1: Identify the first purchase month for each customer
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(sale_date)) AS cohort_month
    FROM fact_sales
    GROUP BY customer_id
),
customer_activities AS (
    -- Step 2: Extract purchase months for all orders
    SELECT
        f.customer_id,
        DATE_TRUNC('month', f.sale_date) AS activity_month
    FROM fact_sales f
    GROUP BY f.customer_id, DATE_TRUNC('month', f.sale_date)
),
cohort_sizes AS (
    -- Step 3: Calculate the size of each cohort
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),
retention_matrix AS (
    -- Step 4: Map cohort customers to subsequent purchase months
    SELECT
        cc.cohort_month,
        EXTRACT(MONTH FROM age(ca.activity_month, cc.cohort_month)) + 
        (12 * EXTRACT(YEAR FROM age(ca.activity_month, cc.cohort_month))) AS period_index,
        COUNT(DISTINCT ca.customer_id) AS active_customer_count
    FROM customer_cohorts cc
    JOIN customer_activities ca ON cc.customer_id = ca.customer_id
    GROUP BY cc.cohort_month, period_index
)
SELECT
    TO_CHAR(r.cohort_month, 'YYYY-MM') AS cohort,
    cs.cohort_size,
    r.period_index AS retention_period_month,
    r.active_customer_count,
    ROUND((r.active_customer_count::numeric / cs.cohort_size::numeric) * 100, 2) AS retention_rate_percentage
FROM retention_matrix r
JOIN cohort_sizes cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.period_index;

-- ==========================================
-- 5. LOGISTICS & OPERATIONAL PERFORMANCE
-- Target: Review shipping carrier speeds and delivery latencies by region
-- ==========================================
SELECT
    s.shipping_carrier,
    s.shipping_service_level,
    s.warehouse_location,
    COUNT(f.sale_id) AS total_shipments,
    AVG(f.shipping_delay_days) AS avg_delivery_delay_days,
    MAX(f.shipping_delay_days) AS max_delivery_delay_days
FROM fact_sales f
JOIN dim_shipping s ON f.shipping_id = s.shipping_id
GROUP BY s.shipping_carrier, s.shipping_service_level, s.warehouse_location
ORDER BY avg_delivery_delay_days ASC;

-- ==========================================
-- 6. PAYMENT MODE POPULARITY & SHARE
-- Target: Share of transaction volume and sales by payment gateway methods
-- ==========================================
SELECT
    p.payment_method,
    p.card_provider,
    COUNT(f.sale_id) AS transaction_count,
    SUM(f.total_sale_amount) AS transaction_revenue,
    ROUND(AVG(f.total_sale_amount), 2) AS avg_transaction_value
FROM fact_sales f
JOIN dim_payments p ON f.payment_id = p.payment_id
GROUP BY p.payment_method, p.card_provider
ORDER BY transaction_revenue DESC;
