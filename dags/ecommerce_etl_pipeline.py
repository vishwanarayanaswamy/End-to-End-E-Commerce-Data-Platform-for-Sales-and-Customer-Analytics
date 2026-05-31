"""
Airflow Orchestration DAG for E-Commerce Data Warehouse ETL Pipeline
Schedules: Daily at midnight (0 0 * * *)
Author: Sheerin Banu Shiek Mohamed
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import os

# Default arguments for the DAG tasks
default_args = {
    'owner': 'sheerin',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 25),
    'email': ['sheerin.mohamed@ecommerce-dw.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def verify_dataset_exists():
    """Validates presence of raw file in staging landing zone."""
    input_file = "/Users/sandeepjohn/koushik/cleaned_retail_data.csv"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Landing zone error: Cleaned data file not found at {input_file}")
    print(f"[SUCCESS] Staging file exists. Ready to initiate ingestion.")

# Define the DAG
with DAG(
    'ecommerce_etl_pipeline',
    default_args=default_args,
    description='Automated extraction, transformation, and warehouse loading of retail data',
    schedule_interval='0 0 * * *',  # Run daily at midnight
    catchup=False,
    tags=['retail', 'dw', 'etl'],
) as dag:

    # Task 1: Check if staging CSV exists
    check_raw_file = PythonOperator(
        task_id='verify_raw_dataset',
        python_callable=verify_dataset_exists,
    )

    # Task 2: Run Python ETL Pipeline Script
    run_etl_pipeline = BashOperator(
        task_id='execute_etl_pipeline',
        bash_command='python3 /Users/sandeepjohn/koushik/src/processing/etl.py --input /Users/sandeepjohn/koushik/cleaned_retail_data.csv',
    )

    # Task 3: Verify load by executing analytics validation
    verify_database_imports = BashOperator(
        task_id='verify_warehouse_analytics',
        bash_command='psql -h localhost -d ecommerce_dw -U postgres -f /Users/sandeepjohn/koushik/src/database/analytics_queries.sql > /Users/sandeepjohn/koushik/data/quarantine/last_analytics_report.log',
    )

    # Sequential execution flow
    check_raw_file >> run_etl_pipeline >> verify_database_imports
