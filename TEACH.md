# 🎓 The Beginner's Data Engineering Companion
## Capstone Project: End-to-End E-Commerce Data Platform

Welcome to your first day as a Data Engineer! If you know basic Python but have never built a database, orchestrated pipelines, or scaled data systems on the cloud, **this manual is for you**. We will break down every single component, file, and technology in this project using friendly analogies, simple English, and zero confusing corporate jargon.

---

## 1. What Problem Does This Project Solve?

Imagine you own a rapidly growing online store. 
* **The Mess:** Every time a customer places an order, their profile goes into a spreadsheet. Your payments are saved in a third-party gateway portal. Your delivery tracking numbers are written on a whiteboard, and your inventory stock counts are in a text file.
* **The Manual Chaos:** If you want to know which product category generated the highest net margins in India last month, you must download three separate CSV files, copy-paste them into Excel, write complex `VLOOKUP` formulas, and manually clean up missing dates or typos. By the time you get the answer, it is already out of date!
* **The Solution:** This project automatically builds an **integrated conveyor belt** (the pipeline) that scoops up all these messy files, cleans them of errors, stores them in a single digital warehouse, and updates a beautiful display window (Power BI) in real-time.

---

## 2. The Complete End-to-End Flow

Here is the digital layout of how data flows through our platform, from raw files on your laptop all the way to cloud dashboards:

```
┌──────────────────────┐
│  1. Raw CSV Files    │  <-- Messy incoming order logs
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  2. Apache NiFi      │  <-- The automatic vacuum cleaner
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  3. Staging Area     │  <-- Temporary landing zone
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  4. Apache Airflow   │  <-- The shift manager (alarms & clocks)
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  5. Python ETL       │  <-- The kitchen chef (cleans, validates)
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  6. PostgreSQL       │  <-- The central cloud warehouse
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  7. Power BI         │  <-- The interactive visual shop window
└──────────────────────┘
```

### Every Step Explained Simply:
1. **Raw CSV Files:** Messy receipts written by individual stores.
2. **Apache NiFi:** *What is it?* An automated file mover. *Why we need it:* It vacuums files as soon as they appear. *Without it:* You would have to drag-and-drop files manually.
3. **Staging Area:** A folder holding files prior to cleaning.
4. **Apache Airflow:** *What is it?* The scheduling manager. *Why we need it:* It schedules the cleaning jobs and reports errors. *Without it:* You would have to execute the scripts yourself at midnight.
5. **Python ETL:** *What is it?* The cleaning script. *Why we need it:* It checks for missing IDs, reformats columns, and flags errors. *Without it:* Bad data would break your database.
6. **PostgreSQL:** *What is it?* The database warehouse. *Why we need it:* It stores everything in structured tables. *Without it:* You are back to copy-pasting Excel files.
7. **Power BI:** *What is it?* The reporting dashboard. *Why we need it:* It translates tables into simple charts. *Without it:* Business managers would have to write raw SQL to read data.

---

## 3. Follow One CSV File Through The Entire System

Let's follow a fictional file: `orders_may.csv` containing raw store orders:

```text
InvoiceNo,StockCode,Description,Quantity,Year,Month,Day,Hour,CustomerID,Country,Region,PaymentMode
100002,6890,KEYBOARD,2,2025,5,30,14,28625,UK,North,Cash
```

### 1. Ingestion Checkpoint (NiFi)
NiFi stands guard, listening to a directory. The second `orders_may.csv` is dropped into `/data/raw/`, NiFi picks it up, logs its timestamp, and copies it to our pipeline staging area.

### 2. Schedule Trigger (Airflow)
At midnight, Airflow's clock rings. It checks if the staging area has the new file. Seeing `orders_may.csv`, it kicks off Task 2: the Python ETL script.

### 3. The Clean & Validate (Python ETL)
The Python script opens `orders_may.csv` and reads our line:
* It looks at `Year: 2025`, `Month: 5`, `Day: 30` and binds them into a proper calendar date: `2025-05-30`.
* It verifies that `Quantity` (`2`) is greater than zero. (Passes!)
* It verifies that the `CustomerID` (`28625`) and `StockCode` (`6890`) exist. (Passes!)
* It automatically creates dummy profile items: `first_name = "CustomerFirst_28625"`, `email = "customer_28625@retail-platform.com"`.

### 4. Database Loading (PostgreSQL)
The ETL opens a database transaction:
1. It inserts the customer into `dim_customers`.
2. It inserts the keyboard into `dim_products`.
3. It inserts the date into `dim_dates`.
4. It inserts the transaction details into `fact_sales`, generating a unique hash `sale_id`.

### 5. Reporting (Power BI)
Your friend opens Power BI. The dashboard queries Neon/Postgres, reads the new `fact_sales` row, and updates the total gross revenue count dynamically!

---

## 4. Repository Walkthrough

Here is a map of every single folder and file in your repository:

### 📁 `.env.example`
* **What is it?** A blueprint template listing environment variables.
* **Why does it exist?** It tells developers what database passwords and server details are needed without exposing secret credentials on GitHub.
* **Who uses it?** Developers setting up their environment.
* **When does it run?** Only once, during project installation.
* **What breaks if deleted?** It doesn't break the running code, but new developers won't know how to configure their `.env` files.

### 📁 `docker-compose.yml`
* **What is it?** A config file mapping out the multi-service container network.
* **Why does it exist?** It boots up Airflow, NiFi, and PostgreSQL together, establishing connections between them automatically.
* **Who uses it?** Docker Compose engine.
* **When does it run?** When you run `docker-compose up -d`.
* **What breaks if deleted?** You can no longer run the containerized stack in one go; you would have to install all services manually on your laptop.

### 📁 `docker/postgres/init-databases.sh`
* **What is it?** A shell script to create multiple databases inside the Postgres container.
* **Why does it exist?** Standard Postgres containers only create one database. This script ensures both `airflow` and `ecommerce_dw` databases are created on start.
* **Who uses it?** PostgreSQL container entrypoint.
* **When does it run?** Upon container startup.
* **What breaks if deleted?** Airflow will fail to launch because the `airflow` database won't exist.

### 📁 `dags/ecommerce_etl_pipeline.py`
* **What is it?** The Apache Airflow workflow diagram definition.
* **Why does it exist?** It schedules the pipeline, tells Airflow what to run, and defines task dependencies.
* **Who uses it?** Apache Airflow scheduler.
* **When does it run?** Scheduled daily at midnight.
* **What breaks if deleted?** The ETL pipeline will no longer run automatically on a schedule.

### 📁 `src/database/schema.sql`
* **What is it?** The database design script (DDL).
* **Why does it exist?** It creates the dimension and fact tables, defines columns, keys, check constraints, and performance indexes.
* **Who uses it?** The database administrator or the migration script.
* **When does it run?** Only when setting up or resetting the database warehouse.
* **What breaks if deleted?** You cannot create the warehouse database tables, causing the ETL script to crash.

### 📁 `src/database/analytics_queries.sql`
* **What is it?** A query suite calculating sales summaries, categories, cohorts, and operations metrics.
* **Why does it exist?** It extracts business answers from the database to populate Power BI reports.
* **Who uses it?** Data Analysts and Power BI dashboards.
* **When does it run?** On demand, or during report updates.
* **What breaks if deleted?** Analysts will have to write queries from scratch to check warehouse health.

### 📁 `src/processing/etl.py`
* **What is it?** The core Python ETL pipeline script.
* **Why does it exist?** It reads the raw staging files, cleans data columns, generates dimension attributes, filters anomalies, and loads the database warehouse.
* **Who uses it?** The pipeline scheduler (Airflow or manual shell execution).
* **When does it run?** Triggered daily or on demand.
* **What breaks if deleted?** You can no longer transform or load raw CSV files into your database warehouse.

### 📁 `src/tests/test_database.py`
* **What is it?** The quality testing assertions script.
* **Why does it exist?** It connects to the database and verifies that no bad data (negative values, orphaned records) snuck into your warehouse.
* **Who uses it?** Developers running quality controls.
* **When does it run?** During code integration or deployment.
* **What breaks if deleted?** You won't know if bad records have bypassed your filters and corrupted your warehouse database.

### 📁 `CLOUD_DEPLOYMENT.md`
* **What is it?** Step-by-step cloud setup reference guide.
* **Why does it exist?** It documents how to host your PostgreSQL database on Neon or Supabase and hook up Power BI.
* **Who uses it?** Developers deploying the project to the cloud.
* **When does it run?** Read on demand.
* **What breaks if deleted?** Users won't have a simple reference guide for cloud hosting.

---

## 5. Deep Dive Into Every Technology

Let's study each technology used in our project:

### 🐳 Docker & Docker Compose
* **Technical Definition:** A platform that uses OS-level virtualization to deliver software in packages called containers.
* **Why We Use It:** It packages Postgres, Airflow, and NiFi so they run exactly the same way on any computer.
* **Alternative:** Installing everything manually on your system.
* **Problem It Solves:** Avoids the "but it works on my computer!" bug.
* **Beginner Analogy:** Docker is like modular kitchen blocks. Instead of building a custom stove, fridge, and sink on your floor, you just drop in pre-built blocks that plug in instantly.
* **Without It:** You would spend hours installing, updating, and troubleshooting database and pipeline packages locally.

### ⏱️ Apache Airflow
* **Technical Definition:** An open-source platform to programmatically author, schedule, and monitor workflows.
* **Why We Use It:** To automate our data cleaning schedules and retry failed steps.
* **Alternative:** Cron jobs or manual execution.
* **Problem It Solves:** Prevents data gaps due to human scheduling errors.
* **Beginner Analogy:** Airflow is like a kitchen shift manager. It checks if the vegetables have arrived, tells the chef to start cooking, setting off an alarm if the chef burns the food!
* **Without It:** You would have to wake up and click "Run Script" manually.

### 🚚 Apache NiFi
* **Technical Definition:** An easy-to-use, powerful, and reliable system to process and distribute data.
* **Why We Use It:** To listen to folders and instantly ingest files the second they arrive.
* **Alternative:** Python folder listeners or manual FTP uploads.
* **Problem It Solves:** Automates the physical movement of messy incoming raw files.
* **Beginner Analogy:** NiFi is like an automated robot vacuum cleaner. It spots dust (raw files) on the floor, sucks it up, and empties it in the trash can (staging folder) automatically.
* **Without It:** You would have to drag files into your project staging directories manually.

### 🐍 Python & Pandas
* **Technical Definition:** Python is a high-level coding language. Pandas is its data analysis library.
* **Why We Use It:** To load, filter, transform, and clean raw data columns.
* **Alternative:** R, Scala, or raw SQL functions.
* **Problem It Solves:** Standardizes text and handles math logic on millions of records efficiently.
* **Beginner Analogy:** Pandas is like a superpowered Excel sheet. It lets you write formulas, remove blank rows, and calculate totals in a fraction of a second using a few simple lines of code.
* **Without It:** You would have to write raw Python loops which are extremely slow and complex.

### 🗄️ PostgreSQL & SQL
* **Technical Definition:** PostgreSQL is an open-source object-relational database. SQL is the language used to communicate with it.
* **Why We Use It:** To store clean records securely in relational tables.
* **Alternative:** MySQL, SQLite, MongoDB.
* **Problem It Solves:** Stores data safely, enforces relationships, and allows fast lookups.
* **Beginner Analogy:** SQL is like talking to a massive filing cabinet using standard English commands (like `"SELECT file FROM cabinet WHERE date = today"`).
* **Without It:** You would have to search heavy Excel sheets manually.

---

## 6. Database & Warehousing Deep Dive

A beginner often asks: *"Why do we need a database? Can't we just use CSV spreadsheets?"*

### Why CSV files are not enough:
1. **Size Limits:** A CSV file slows down and crashes if it grows beyond a few hundred thousand rows. PostgreSQL can store **billions** of rows smoothly.
2. **Speed:** Finding a specific customer in a CSV file requires reading the entire file line-by-line from top to bottom. A database uses **Indexes** (like a book index) to jump straight to the row in a millisecond.
3. **Data Protection:** Spreadsheets allow typos—someone could write `"Ten"` instead of `10` in a quantity column. A database enforces **Check Constraints** that reject any incorrect data types.

### OLTP vs. OLAP
```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│     OLTP (Online Transactional)  │     │     OLAP (Online Analytical)    │
│  - Optimised for speed.         │ ──> │  - Optimised for analytics.     │
│  - e.g. Placing a single order. │     │  - e.g. Monthly sales trends.   │
└─────────────────────────────────┘     └─────────────────────────────────┘
```
* **OLTP:** Focused on writing single transactions quickly. E.g., when a user buys a product, the database quickly records that single purchase.
* **OLAP (Data Warehouse):** Focused on analyzing millions of historical records. It groups data into a single source of truth optimized for reading and business reporting.

---

## 7. Star Schema Deep Dive

When designing a Data Warehouse, we arrange our tables in a **Star Schema**. 

### Why is it called a Star Schema?
It is called a Star Schema because your central table is surrounded by lookup tables, resembling a star:

```
          ┌────────────────┐
          │  dim_customers │
          └───────┬────────┘
                  │
  ┌───────────────┼───────────────┐
  │                               │
┌─┴────────────┐  │  ┌────────────┴─┐
│ dim_products ├──┼──┤ dim_shipping │
└──────────────┘  │  └──────────────┘
            ┌─────┴──────┐
            │ fact_sales │
            └─────┬──────┘
  ┌───────────────┼───────────────┐
  │                               │
┌─┴────────────┐  │  ┌────────────┴─┐
│ dim_payments ├──┴──┤  dim_dates   │
└──────────────┘     └──────────────┘
```

### Fact Table vs. Dimension Table
* **Fact Table (`fact_sales`):** The center of the star. It stores the actual **numeric measurements** of a transaction (e.g. `quantity_ordered`, `unit_price`, `discount_amount`, `total_sale_amount`).
* **Dimension Table (e.g., `dim_customers`):** The points of the star. They store the **descriptive attributes** (e.g. customer name, product category, shipping carrier, date name).

### How Joins Work (An Example)
Instead of writing customer details (name, email, city) over and over again on every invoice line, we write a small **ID** (e.g., `customer_id = 28625`) in the `fact_sales` table.
When we run our analytics query, we **join** the tables together:

```sql
SELECT f.order_id, c.first_name, f.total_sale_amount
FROM fact_sales f
JOIN dim_customers c ON f.customer_id = c.customer_id;
```
This is extremely efficient: it keeps the `fact_sales` table lightweight, and allows fast lookups on dimension attributes!

---

## 8. Airflow Deep Dive

Airflow orchestrates tasks using a **DAG** (Directed Acyclic Graph):
* **Directed:** Tasks flow in a specific direction (Task A must run before Task B).
* **Acyclic:** You cannot have loops (Task B cannot point back to Task A, creating an infinite loop).
* **Graph:** A visual mapping of nodes (tasks) and arrows (dependencies).

Let's look at the actual DAG in this project ([ecommerce_etl_pipeline.py](file:///Users/sandeepjohn/koushik/dags/ecommerce_etl_pipeline.py)) line-by-line:

```python
# default_args defines what happens when tasks run, retry, or fail
default_args = {
    'owner': 'sheerin',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 25),
    'email_on_failure': True,
    'retries': 2,                 # If a task fails, try again up to 2 times
    'retry_delay': timedelta(minutes=5), # Wait 5 minutes between retries
}

# The main DAG container
with DAG(
    'ecommerce_etl_pipeline',
    default_args=default_args,
    schedule_interval='0 0 * * *', # Daily at midnight
    catchup=False,
) as dag:

    # Task 1: Check if staging CSV exists
    check_raw_file = PythonOperator(
        task_id='verify_raw_dataset',
        python_callable=verify_dataset_exists, # Executes our python check function
    )

    # Task 2: Run Python ETL Pipeline Script
    run_etl_pipeline = BashOperator(
        task_id='execute_etl_pipeline',
        bash_command='python3 /Users/sandeepjohn/koushik/src/processing/etl.py', # Fires off the chef script!
    )

    # Task 3: Verify load by executing analytics validation
    verify_database_imports = BashOperator(
        task_id='verify_warehouse_analytics',
        bash_command='psql -d ecommerce_dw -f src/database/analytics_queries.sql',
    )

    # Dependencies (Task sequence mapping)
    check_raw_file >> run_etl_pipeline >> verify_database_imports
```

---

## 9. ETL Deep Dive

ETL stands for **Extract, Transform, and Load**:

```
  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
  │  1. EXTRACT  │  ──>  │  2. TRANSFORM│  ──>  │   3. LOAD    │
  │ - Read file  │       │ - Clean data │       │ - Save to DB │
  └──────────────┘       └──────────────┘       └──────────────┘
```

Let's study the exact transformations applied in our ETL pipeline code ([etl.py](file:///Users/sandeepjohn/koushik/src/processing/etl.py)):

### Transformation 1: Unified Date Construction
* **What it does:** Combines `Year`, `Month`, and `Day` integer columns into a single `sale_date` timestamp.
* **Why it exists:** Dates are chronological anchors. Joining on three separate columns is incredibly slow and messy.
* **Before:** `Year: 2025`, `Month: 5`, `Day: 30`
* **After:** `2025-05-30` (DATE type)

### Transformation 2: Deterministic Mock Data Generation
* **What it does:** Generates customer contact details and logistical entries based on transaction values.
* **Why it exists:** Keeps the Star Schema visual reports rich and complete even when raw transactional fields are missing.
* **Before:** `CustomerID = 28625`
* **After:** `first_name = "CustomerFirst_28625"`, `email = "customer_28625@retail-platform.com"`

---

## 10. Data Quality Rules

Our ETL script acts as a gatekeeper, validating and separating bad records to prevent database corruption.

### The Ingestion Quality Rules:
1. **Primary Key Integrity:** Null values are forbidden in transaction keys (`CustomerID`, `StockCode`, `InvoiceNo`, `sale_date`).
   * *Bad Data:* `CustomerID = None`, `StockCode = 6890`
   * *Action:* Record is immediately isolated.
2. **Financial Bounds:** Values in `UnitPrice`, `Quantity`, and `Revenue` must be greater than zero.
   * *Bad Data:* `Quantity = -2`, `UnitPrice = 1200`
   * *Action:* Record is sent to quarantine.
3. **DateTime Accuracy:** Transaction dates cannot exceed the current local date, nor can they pre-date `2020-01-01`.
   * *Bad Data:* `sale_date = 2035-12-25` (Future Date)
   * *Action:* Isolated and quarantined.

### The Quarantine Folder
Instead of letting the entire pipeline crash, all bad rows are automatically written to `/Users/sandeepjohn/koushik/data/quarantine/bad_records.csv` for developers to review later. The pipeline continues running smoothly for good records!

---

## 11. Incremental Loads & Idempotency

### What is Idempotency?
> **Definition:** A pipeline is **idempotent** if running it multiple times on the same input data produces the exact same result without duplicate records.

### The Duplicates Problem
If you run a simple pipeline script twice, it might insert the same 10,000 rows again, double-counting your sales revenue!

### The Solution: UPSERT (`ON CONFLICT`)
In our loading script, we use SQL's `ON CONFLICT` clause:
```sql
INSERT INTO fact_sales (sale_id, customer_id, total_sale_amount)
VALUES ('abc123xyz', '28625', 10182.28)
ON CONFLICT (sale_id) DO UPDATE SET
    total_sale_amount = EXCLUDED.total_sale_amount;
```
* **How it works:** If PostgreSQL spots that `sale_id = 'abc123xyz'` already exists, it doesn't insert a duplicate row. Instead, it just updates the existing row with the latest values. 
* This makes your pipeline safe to run at any time!

---

## 12. Docker Container Communication

In our container environment ([docker-compose.yml](file:///Users/sandeepjohn/koushik/docker-compose.yml)), we coordinate four separate services:

| Container | Purpose | Port | Dependencies |
| :--- | :--- | :--- | :--- |
| **`postgres`** | Hosts DW and Metadata databases | `5432` | None |
| **`nifi`** | Raw File Ingestion | `8080` | None |
| **`airflow-webserver`** | Workflow scheduler UI | `8082` | `postgres` (Healthy) |
| **`airflow-scheduler`** | DAG schedule executor | *Internal* | `postgres` (Healthy) |

### How Containers Talk to Each Other:
Docker creates an internal virtual network. Instead of using `localhost`, containers talk to each other using their service names. For example, Airflow connects to PostgreSQL using the address `postgres:5432`.

---

## 13. SQL Analytics Walkthrough

Let's study the critical queries in [analytics_queries.sql](file:///Users/sandeepjohn/koushik/src/database/analytics_queries.sql):

### Query 1: Executive Sales Overview
* **Business Question:** What is our total revenue, order count, and Average Order Value (AOV)?
* **Tables Involved:** `fact_sales`
* **Logic:** Count distinct `order_id`s, sum transaction sales amounts, and average AOV.
* **Output:** A single row showing total orders of `10,000` and gross revenue of `$101,822,804.00`.

### Query 2: Product Performance by Category
* **Business Question:** Which category makes the highest sales share?
* **Tables Involved:** `fact_sales` and `dim_products` (joined on `product_id`).
* **Logic:** Groups transactions by category, sums revenues, and calculates percentages using window functions:
  ```sql
  SUM(total_sale_amount) / SUM(SUM(total_sale_amount)) OVER () * 100
  ```
* **Output:** Accesssories accounts for `50.89%` and Electronics accounts for `49.11%`.

---

## 14. Power BI Deep Dive

Power BI brings our cloud data warehouse to life.

### 1. Connection
Power BI connects directly to your cloud PostgreSQL database (Neon/Supabase) via port `5432`.
It uses the **Import** connectivity mode, loading `fact_sales` and our 5 dimension tables into memory.

### 2. Business KPIs Populated
* **Customer Lifetime Value (CLV):** Calculated dynamically by multiplying a customer's average order value by their purchase frequency.
* **Cohort Churn Ratios:** Tracking how many customers return to place orders in months 1, 2, and 3 after their initial purchase.
* **Logistics Delays:** Highlighting average delivery delays by shipping carriers and region to locate logistical bottlenecks.

---

## 15. Explain This Project In A Job Interview

Here are standard interview pitches depending on the time you have:

### 30-Second Elevator Pitch
> *"I designed and built a containerized, end-to-end E-Commerce Data Platform. The system automatically ingests messy transactional CSV records, runs them through a Python-based validation and transformation pipeline, and loads them into a highly optimized PostgreSQL Star Schema warehouse. This single source of truth is connected directly to a cloud Power BI dashboard to track key business metrics like AOV and monthly cohort retention."*

### 2-Minute Explanation
> *"In my project, I established a robust ingestion workflow. Raw transactional logs are captured automatically. I designed a Directed Acyclic Graph in Apache Airflow that automates a daily ETL pipeline written in Python and Pandas. The pipeline enforces strict data quality validations, filtering out corrupt dates and negative prices, while quarantining outliers. The clean data is loaded idempotently via UPSERT rules into a PostgreSQL Star Schema warehouse. I created performance indexes on the fact table foreign keys to optimize joins. Finally, I authored a query suite calculating customer cohort retention and linked the live cloud database directly to Power BI dashboards."*

---

### Common Interviewer Questions & Answers

#### Q: Why did you choose a Star Schema design instead of keeping it flat?
> **A:** *"A flat table contains massive redundancy, repeating customer names and descriptions millions of times, which consumes excessive storage. A Star Schema separates attributes into specialized dimension tables, keeping the central fact table incredibly narrow and fast. Creating indexes on foreign keys accelerates database joins, making analytical reporting significantly faster."*

#### Q: How did you ensure your ETL pipeline was idempotent?
> **A:** *"I generated a unique, deterministic hash `sale_id` based on the combination of `InvoiceNo` and `StockCode`. During the load phase, I utilized SQL's `ON CONFLICT (sale_id) DO UPDATE` command. If the script is re-run, it updates existing records instead of inserting duplicates, preventing double-counting of revenues."*

---

## 16. Beginner Learning Roadmap

Now that you have completed this project, here is your path to becoming an expert Data Engineer:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   1. SQL     │ ──> │  2. Python   │ ──> │  3. Airflow  │ ──> │   4. Spark   │
│ (Aggregation)│     │   (Pandas)   │     │(Orchestration)     │(Big Data scale)
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **SQL (Advanced):** Focus on Window Functions, CTEs, and query indexing. This is the absolute foundation of data warehouses.
2. **Python & Pandas:** Build custom scripts to clean and merge unstructured JSON and Excel data.
3. **Airflow DAG Design:** Master dynamic DAG generation, scheduling rules, and sensor checks.
4. **Apache Spark:** Once your dataset grows from megabytes to gigabytes, learn Spark to scale calculations across distributed computer nodes!
