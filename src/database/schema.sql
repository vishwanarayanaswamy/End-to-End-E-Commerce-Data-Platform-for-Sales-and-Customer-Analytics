-- PostgreSQL Data Warehouse Schema Definition (Star Schema Model)
-- Capstone Project: End-to-End E-Commerce Data Platform
-- Author: Koushik Raj Singh

-- Drop existing tables to ensure clean deployment (order matters due to constraints)
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_dates CASCADE;
DROP TABLE IF EXISTS dim_payments CASCADE;
DROP TABLE IF EXISTS dim_shipping CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;

-- 1. Customers Dimension
CREATE TABLE dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    country VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products Dimension
CREATE TABLE dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    original_price NUMERIC(10, 2) NOT NULL CHECK (original_price >= 0),
    inventory_stock INT NOT NULL CHECK (inventory_stock >= 0)
);

-- 3. Shipping Details Dimension
CREATE TABLE dim_shipping (
    shipping_id VARCHAR(50) PRIMARY KEY,
    shipping_carrier VARCHAR(100) NOT NULL,
    shipping_service_level VARCHAR(50) NOT NULL,
    warehouse_location VARCHAR(100) NOT NULL
);

-- 4. Payments Dimension
CREATE TABLE dim_payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL,
    card_provider VARCHAR(50),
    billing_country VARCHAR(100) NOT NULL
);

-- 5. Dates Dimension (for granular time-series analytics)
CREATE TABLE dim_dates (
    date_actual DATE PRIMARY KEY,
    epoch BIGINT NOT NULL,
    day_suffix VARCHAR(5) NOT NULL,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    day_name VARCHAR(20) NOT NULL,
    day_of_month INT NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_of_year INT NOT NULL CHECK (day_of_year BETWEEN 1 AND 366),
    week_of_year INT NOT NULL CHECK (week_of_year BETWEEN 1 AND 53),
    month_actual INT NOT NULL CHECK (month_actual BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    quarter_actual INT NOT NULL CHECK (quarter_actual BETWEEN 1 AND 4),
    year_actual INT NOT NULL CHECK (year_actual >= 2020)
);

-- 6. Sales Transaction Fact Table
CREATE TABLE fact_sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES dim_customers(customer_id) ON DELETE RESTRICT,
    product_id VARCHAR(50) NOT NULL REFERENCES dim_products(product_id) ON DELETE RESTRICT,
    shipping_id VARCHAR(50) NOT NULL REFERENCES dim_shipping(shipping_id) ON DELETE RESTRICT,
    payment_id VARCHAR(50) NOT NULL REFERENCES dim_payments(payment_id) ON DELETE RESTRICT,
    sale_date DATE NOT NULL REFERENCES dim_dates(date_actual) ON DELETE RESTRICT,
    order_id VARCHAR(50) NOT NULL,
    quantity_ordered INT NOT NULL CONSTRAINT chk_positive_qty CHECK (quantity_ordered > 0),
    unit_price NUMERIC(10, 2) NOT NULL CONSTRAINT chk_positive_price CHECK (unit_price > 0),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0 CONSTRAINT chk_positive_discount CHECK (discount_amount >= 0),
    total_tax NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (total_tax >= 0),
    total_sale_amount NUMERIC(10, 2) NOT NULL CONSTRAINT chk_positive_sale CHECK (total_sale_amount > 0),
    shipping_delay_days INT NOT NULL DEFAULT 0 CHECK (shipping_delay_days >= 0)
);

-- Performance Optimization Indexes (OLAP acceleration)
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX idx_fact_sales_date ON fact_sales(sale_date);
CREATE INDEX idx_fact_sales_shipping ON fact_sales(shipping_id);
CREATE INDEX idx_fact_sales_payment ON fact_sales(payment_id);
CREATE INDEX idx_dim_customers_country ON dim_customers(country);
CREATE INDEX idx_dim_products_category ON dim_products(category);
