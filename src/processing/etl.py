#!/usr/bin/env python3
"""
ETL Pipeline for the E-Commerce Data Platform
Extracts, transforms, validates, and loads clean retail CSV data into PostgreSQL Star Schema.
Author: Vishwa Narayanaswamy & Sheerin Banu Shiek Mohamed
"""

import os
import argparse
import datetime
import hashlib
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run ETL Pipeline for E-Commerce Data Warehouse")
    parser.add_argument("--input", default="cleaned_retail_data.csv", help="Path to cleaned input CSV file")
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", default=5432, type=int, help="PostgreSQL port")
    parser.add_argument("--dbname", default="ecommerce_dw", help="PostgreSQL database name")
    parser.add_argument("--user", default="postgres", help="PostgreSQL username")
    parser.add_argument("--password", default="", help="PostgreSQL password")
    return parser.parse_args()

def check_and_create_quarantine_dir():
    quarantine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "quarantine"))
    os.makedirs(quarantine_dir, exist_ok=True)
    return quarantine_dir

def connect_db(args):
    """Establishes database connection with standard parameters."""
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.dbname,
        user=args.user,
        password=args.password
    )

def extract_data(filepath):
    print(f"[*] Extracting raw data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")
    return pd.read_csv(filepath)

def transform_and_validate(df, quarantine_dir):
    print("[*] Starting data transformations & quality validations...")
    
    # 1. Parse unified transactional sale_date
    print(" -> Constructing transactional dates...")
    df['sale_date_str'] = df.apply(lambda row: f"{int(row['Year'])}-{int(row['Month']):02d}-{int(row['Day']):02d}", axis=1)
    df['sale_date'] = pd.to_datetime(df['sale_date_str'], format='%Y-%m-%d', errors='coerce').dt.date
    
    initial_count = len(df)
    
    # 2. Data Quality Assertions
    # Quality Rule 1: Primary Key Integrity (Nulls forbidden in keys)
    pk_mask = df['CustomerID'].notna() & df['StockCode'].notna() & df['InvoiceNo'].notna() & df['sale_date'].notna()
    
    # Quality Rule 2: Financial Bounds (Unit prices, quantities, revenues must be positive)
    financial_mask = (df['Quantity'] > 0) & (df['UnitPrice'] > 0) & (df['Revenue'] > 0)
    
    # Quality Rule 3: DateTime Accuracy (No future dates, no pre-platform launches)
    today = datetime.date.today()
    launch_date = datetime.date(2020, 1, 1)
    date_mask = df['sale_date'].apply(lambda d: pd.notna(d) and (launch_date <= d <= today))
    
    # Identify good and bad records
    valid_mask = pk_mask & financial_mask & date_mask
    
    good_records = df[valid_mask].copy()
    bad_records = df[~valid_mask].copy()
    
    # If bad records exist, write to quarantine
    if len(bad_records) > 0:
        quarantine_file = os.path.join(quarantine_dir, "bad_records.csv")
        bad_records.to_csv(quarantine_file, index=False)
        print(f" [WARNING] Flags triggered! Quarantined {len(bad_records)} bad records to: {quarantine_file}")
    
    print(f" -> Retained {len(good_records)} of {initial_count} records (Success rate: {len(good_records)/initial_count:.2%})")
    
    return good_records

def generate_dimensions(df):
    print("[*] Generating Star Schema dimension tables...")
    
    # 1. Generate Customers Dimension (with deterministic name/contact info)
    print(" -> Generating dim_customers...")
    unique_cust = df[['CustomerID', 'Country', 'Region']].drop_duplicates(subset=['CustomerID']).copy()
    dim_customers = []
    for _, r in unique_cust.iterrows():
        c_id = str(int(r['CustomerID']))
        dim_customers.append((
            c_id,
            f"CustomerFirst_{c_id}",
            f"CustomerLast_{c_id}",
            f"customer_{c_id}@retail-platform.com",
            f"+1-555-{int(r['CustomerID']) % 10000:04d}",
            r['Country'],
            r['Region']
        ))
        
    # 2. Generate Products Dimension (with deterministic brand/stock)
    print(" -> Generating dim_products...")
    unique_prod = df[['StockCode', 'Description', 'ProductCategory', 'UnitPrice']].drop_duplicates(subset=['StockCode']).copy()
    dim_products = []
    for _, r in unique_prod.iterrows():
        p_id = str(int(r['StockCode']))
        dim_products.append((
            p_id,
            r['Description'],
            r['ProductCategory'],
            f"Brand_{r['ProductCategory'][:3].upper()}",
            float(r['UnitPrice']),
            int((int(r['StockCode']) % 500) + 10) # deterministic inventory stock
        ))
        
    # 3. Generate Shipping Dimension (deterministic details based on Region)
    print(" -> Generating dim_shipping...")
    unique_regions = df[['Region', 'Country']].drop_duplicates().copy()
    dim_shipping = []
    shipping_map = {}
    for _, r in unique_regions.iterrows():
        reg = r['Region']
        cnt = r['Country']
        ship_id = f"SHIP_{reg.upper()}_{cnt.upper()}"
        
        # Deterministic carrier assignments
        if cnt == 'India':
            carrier, level, loc = "Blue Dart", "Express", "WH_Mumbai"
        elif cnt == 'USA':
            carrier, level, loc = "FedEx", "Next-Day", "WH_Chicago"
        elif cnt == 'UK':
            carrier, level, loc = "DHL", "Economy", "WH_London"
        else:
            carrier, level, loc = "UPS", "Standard", "WH_Frankfurt"
            
        dim_shipping.append((ship_id, carrier, level, loc))
        shipping_map[(reg, cnt)] = ship_id
        
    # 4. Generate Payments Dimension (deterministic card providers)
    print(" -> Generating dim_payments...")
    unique_payments = df[['PaymentMode', 'Country']].drop_duplicates().copy()
    dim_payments = []
    payment_map = {}
    for _, r in unique_payments.iterrows():
        pmode = r['PaymentMode']
        cnt = r['Country']
        pay_id = f"PAY_{pmode.upper()}_{cnt.upper()}"
        
        if pmode == 'Card':
            provider = "Visa"
        elif pmode == 'Upi':
            provider = "PhonePe"
        else:
            provider = "Cash_On_Delivery"
            
        dim_payments.append((pay_id, pmode, provider, cnt))
        payment_map[(pmode, cnt)] = pay_id
        
    # 5. Generate Dates Dimension
    print(" -> Generating dim_dates...")
    min_date = df['sale_date'].min()
    max_date = df['sale_date'].max()
    date_range = pd.date_range(start=min_date, end=max_date)
    
    dim_dates = []
    for dt in date_range:
        d = dt.date()
        suffix = "th"
        if d.day in [1, 21, 31]: suffix = "st"
        elif d.day in [2, 22]: suffix = "nd"
        elif d.day in [3, 23]: suffix = "rd"
        
        dim_dates.append((
            d,
            int(dt.timestamp()),
            suffix,
            int(dt.isoweekday()),
            dt.strftime('%A'),
            int(d.day),
            int(dt.dayofyear),
            int(dt.isocalendar()[1]),
            int(d.month),
            dt.strftime('%B'),
            int((d.month - 1) // 3 + 1),
            int(d.year)
        ))
        
    # 6. Generate Sales Fact Records
    print(" -> Generating fact_sales...")
    fact_sales = []
    for _, r in df.iterrows():
        c_id = str(int(r['CustomerID']))
        p_id = str(int(r['StockCode']))
        s_date = r['sale_date']
        order_id = str(int(r['InvoiceNo']))
        
        # Link dynamic lookups
        ship_id = shipping_map.get((r['Region'], r['Country']))
        pay_id = payment_map.get((r['PaymentMode'], r['Country']))
        
        # Generate sale_id via determinisic hash
        hash_seed = f"{order_id}_{p_id}_{s_date}"
        sale_id = hashlib.md5(hash_seed.encode('utf-8')).hexdigest()[:16]
        
        # Computations
        qty = int(r['Quantity'])
        price = float(r['UnitPrice'])
        disc = float(r['Discount'])
        tax = float(round(r['Revenue'] * 0.05, 2)) # 5% tax
        total_rev = float(r['Revenue'])
        
        # Deterministic delay calculations based on hour
        delay = int((int(r['Hour']) % 4) + 1) if r['OrderType'] == 'Online' else 0
        
        fact_sales.append((
            sale_id, c_id, p_id, ship_id, pay_id, s_date,
            order_id, qty, price, disc, tax, total_rev, delay
        ))
        
    return dim_customers, dim_products, dim_shipping, dim_payments, dim_dates, fact_sales

def load_data_warehouse(conn, dims_and_facts):
    print("[*] Establishing clean transaction to load PostgreSQL Data Warehouse...")
    dim_cust, dim_prod, dim_ship, dim_pay, dim_date, fact_sales = dims_and_facts
    
    with conn.cursor() as cur:
        # Load dim_customers using upserts
        print(" -> Loading dim_customers...")
        cust_query = """
            INSERT INTO dim_customers (customer_id, first_name, last_name, email, phone, country, region)
            VALUES %s
            ON CONFLICT (customer_id) DO UPDATE SET
                country = EXCLUDED.country,
                region = EXCLUDED.region;
        """
        execute_values(cur, cust_query, dim_cust)
        
        # Load dim_products
        print(" -> Loading dim_products...")
        prod_query = """
            INSERT INTO dim_products (product_id, product_name, category, brand, original_price, inventory_stock)
            VALUES %s
            ON CONFLICT (product_id) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                category = EXCLUDED.category,
                original_price = EXCLUDED.original_price;
        """
        execute_values(cur, prod_query, dim_prod)
        
        # Load dim_shipping
        print(" -> Loading dim_shipping...")
        ship_query = """
            INSERT INTO dim_shipping (shipping_id, shipping_carrier, shipping_service_level, warehouse_location)
            VALUES %s
            ON CONFLICT (shipping_id) DO UPDATE SET
                shipping_carrier = EXCLUDED.shipping_carrier,
                shipping_service_level = EXCLUDED.shipping_service_level,
                warehouse_location = EXCLUDED.warehouse_location;
        """
        execute_values(cur, ship_query, dim_ship)
        
        # Load dim_payments
        print(" -> Loading dim_payments...")
        pay_query = """
            INSERT INTO dim_payments (payment_id, payment_method, card_provider, billing_country)
            VALUES %s
            ON CONFLICT (payment_id) DO UPDATE SET
                payment_method = EXCLUDED.payment_method,
                card_provider = EXCLUDED.card_provider,
                billing_country = EXCLUDED.billing_country;
        """
        execute_values(cur, pay_query, dim_pay)
        
        # Load dim_dates
        print(" -> Loading dim_dates...")
        date_query = """
            INSERT INTO dim_dates (date_actual, epoch, day_suffix, day_of_week, day_name, day_of_month, day_of_year, week_of_year, month_actual, month_name, quarter_actual, year_actual)
            VALUES %s
            ON CONFLICT (date_actual) DO NOTHING;
        """
        execute_values(cur, date_query, dim_date)
        
        # Load fact_sales
        print(" -> Loading fact_sales...")
        fact_query = """
            INSERT INTO fact_sales (sale_id, customer_id, product_id, shipping_id, payment_id, sale_date, order_id, quantity_ordered, unit_price, discount_amount, total_tax, total_sale_amount, shipping_delay_days)
            VALUES %s
            ON CONFLICT (sale_id) DO UPDATE SET
                quantity_ordered = EXCLUDED.quantity_ordered,
                total_sale_amount = EXCLUDED.total_sale_amount;
        """
        execute_values(cur, fact_query, fact_sales)
        
    conn.commit()
    print("[+] Idempotent ETL Run Finished Successfully! Database loaded.")

def main():
    args = parse_arguments()
    quarantine_dir = check_and_create_quarantine_dir()
    
    try:
        # Extract
        raw_df = extract_data(args.input)
        
        # Transform & Validate
        clean_df = transform_and_validate(raw_df, quarantine_dir)
        
        # Generate dimensions and facts
        dims_and_facts = generate_dimensions(clean_df)
        
        # Load
        conn = connect_db(args)
        load_data_warehouse(conn, dims_and_facts)
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] ETL pipeline execution encountered an error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
