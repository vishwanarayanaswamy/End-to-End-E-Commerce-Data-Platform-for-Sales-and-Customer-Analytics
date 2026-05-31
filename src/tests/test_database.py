"""
Data Quality Validation Test Suite for PostgreSQL Star Schema Warehouse
Run using: pytest src/tests/
Author: Vishwa Narayanaswamy
"""

import pytest
import psycopg2
import datetime

import os

# Connection settings matching ETL default configurations
DB_CONN_STR = f"host={os.getenv('DB_HOST', 'localhost')} port={os.getenv('DB_PORT', '5432')} dbname={os.getenv('DB_NAME', 'ecommerce_dw')} user={os.getenv('DB_USER', 'postgres')} password={os.getenv('DB_PASSWORD', 'postgres')}"

def get_connection():
    return psycopg2.connect(DB_CONN_STR)

@pytest.fixture(scope="module")
def db_conn():
    """Setup connection to database and yield for test assertions."""
    conn = get_connection()
    yield conn
    conn.close()

def test_financial_bounds_validations(db_conn):
    """Quality Rule: Verify no negative values exist in sales or unit pricing fields."""
    with db_conn.cursor() as cur:
        # Check fact_sales constraints
        cur.execute("SELECT COUNT(*) FROM fact_sales WHERE quantity_ordered <= 0 OR unit_price <= 0 OR total_sale_amount <= 0;")
        invalid_count = cur.fetchone()[0]
        assert invalid_count == 0, f"Detected {invalid_count} records violating positive financial boundaries!"

def test_primary_key_integrity(db_conn):
    """Quality Rule: Verify no null IDs exist in dimension or fact primary keys."""
    with db_conn.cursor() as cur:
        # Verify dim_customers
        cur.execute("SELECT COUNT(*) FROM dim_customers WHERE customer_id IS NULL;")
        assert cur.fetchone()[0] == 0, "Nulls found in dim_customers primary key!"

        # Verify dim_products
        cur.execute("SELECT COUNT(*) FROM dim_products WHERE product_id IS NULL;")
        assert cur.fetchone()[0] == 0, "Nulls found in dim_products primary key!"

        # Verify fact_sales
        cur.execute("SELECT COUNT(*) FROM fact_sales WHERE sale_id IS NULL;")
        assert cur.fetchone()[0] == 0, "Nulls found in fact_sales primary key!"

def test_foreign_key_reference_integrity(db_conn):
    """Quality Rule: Verify referential integrity holds with zero orphaned records."""
    with db_conn.cursor() as cur:
        # Verify customer relation
        cur.execute("""
            SELECT COUNT(*) 
            FROM fact_sales f 
            LEFT JOIN dim_customers c ON f.customer_id = c.customer_id 
            WHERE c.customer_id IS NULL;
        """)
        orphaned_customers = cur.fetchone()[0]
        assert orphaned_customers == 0, f"Detected {orphaned_customers} orphaned customer foreign keys in fact table!"

        # Verify product relation
        cur.execute("""
            SELECT COUNT(*) 
            FROM fact_sales f 
            LEFT JOIN dim_products p ON f.product_id = p.product_id 
            WHERE p.product_id IS NULL;
        """)
        orphaned_products = cur.fetchone()[0]
        assert orphaned_products == 0, f"Detected {orphaned_products} orphaned product foreign keys in fact table!"

def test_datetime_boundaries(db_conn):
    """Quality Rule: Verify sales and shipping timestamps are mathematically logical."""
    with db_conn.cursor() as cur:
        today = datetime.date.today()
        launch_date = datetime.date(2020, 1, 1)

        # Retrieve min and max dates in fact table
        cur.execute("SELECT MIN(sale_date), MAX(sale_date) FROM fact_sales;")
        min_date, max_date = cur.fetchone()

        if min_date and max_date:
            assert min_date >= launch_date, f"Detected sale_date {min_date} pre-dating platform launch!"
            assert max_date <= today, f"Detected sale_date {max_date} exceeding current local date!"
