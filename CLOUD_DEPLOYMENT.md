# ☁️ Cloud Database Migration & Power BI Deployment Guide
### Sales and Customer Analytics — E-Commerce Capstone Project

This guide provides a comprehensive, step-by-step walkthrough to deploy your relational **Star Schema E-Commerce Data Platform** to the cloud and connect it to **Power BI Desktop & Power BI Service** for real-time dashboards and analytics.

---

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. Cloud DB    │ ──> │   2. DDL Schema │ ──> │   3. Python ETL │ ──> │   4. Power BI   │
│  (Supabase/Neon)│     │     Migration   │     │    Cloud Load   │     │   Connection    │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 🛠️ Step 1: Initialize Cloud PostgreSQL

We recommend using **Supabase** or **Neon** for a modern, serverless, and completely free PostgreSQL deployment.

### Option A: Neon.tech (Recommended)
1. Sign up for a free account at [Neon](https://neon.tech).
2. Click **Create Project**. Name it `ecommerce-dw`.
3. Select your preferred cloud region (e.g., US East / Europe) and click **Create**.
4. In your Dashboard, locate your **Connection String**. Switch the toggle to **Parameters** and copy the following parameters:
   * **Host:** `ep-XXXXXX.us-east-2.aws.neon.tech`
   * **Database:** `neondb`
   * **Username:** `neondb_owner`
   * **Password:** `[Your Generated Password]`

### Option B: Supabase
1. Sign up at [Supabase](https://supabase.com).
2. Click **New Project** -> Select Organization.
3. Fill in the details:
   * **Name:** `ecommerce-dw`
   * **Database Password:** `[Save this safely]`
4. Click **Create new project** (it takes ~1-2 minutes to provision).
5. Navigate to **Project Settings** -> **Database** and copy your **Connection info**:
   * **Host:** `db.XXXXXX.supabase.co`
   * **Port:** `5432`
   * **Database Name:** `postgres`
   * **User:** `postgres`

---

## 🚀 Step 2: Migrate your Star Schema (DDL)

Deploy the target relational structure using your local `schema.sql` script. Run this from your terminal:

```bash
# Execute remotely on your cloud database instance
psql -h <CLOUD_HOST> -d <CLOUD_DATABASE> -U <CLOUD_USER> -f src/database/schema.sql
```
*(Enter your cloud database password when prompted)*

> [!NOTE]
> This command safely drops any pre-existing fact and dimension tables and deploys standard DDL structures (dimensions, fact table, checks, constraints, and optimized OLAP indexes).

---

## 🔄 Step 3: Run the ETL Pipeline (Load Cloud Warehouse)

Because the Python ETL pipeline we built is fully parameterized and idempotent, loading all 10,000 rows into the cloud is extremely simple. Run the local script pointing to your cloud credentials:

```bash
python3 src/processing/etl.py \
  --input cleaned_retail_data.csv \
  --host <CLOUD_HOST> \
  --dbname <CLOUD_DATABASE> \
  --user <CLOUD_USER> \
  --password <CLOUD_PASSWORD>
```

### What happens behind the scenes:
1. **Extraction:** Loads `cleaned_retail_data.csv` locally.
2. **Validation:** Checks date ranges, PK nulls, and financial bounds (quarantining bad rows if found).
3. **Mock Generator:** Deterministically generates realistic emails, names, shipping details, and card providers to keep the Star Schema visually complete.
4. **Idempotent Loading:** Opens a secure transaction, executes bulk loads, and upserts all dimensional keys and fact sales records directly to your cloud host.

---

## 🧪 Step 4: Verify the Remote Database

Run your business intelligence audit script remotely to check gross revenues and order sizes:

```bash
# Verify cloud calculations
psql -h <CLOUD_HOST> -d <CLOUD_DATABASE> -U <CLOUD_USER> -f src/database/analytics_queries.sql
```
*Verify that **gross_revenue** output matches `$101,822,804.00` and total orders are `10,000`.*

---

## 📊 Step 5: Connect Power BI Desktop

Connect your locally installed Power BI Desktop app directly to the cloud database.

1. Open **Power BI Desktop**.
2. Click **Get Data** -> **More...** -> **Database** -> **PostgreSQL database**.
3. Input your cloud database parameter settings:
   * **Server:** `<CLOUD_HOST>:<PORT>` (e.g. `ep-cool-breeze.neon.tech:5432`)
   * **Database:** `<CLOUD_DATABASE>` (e.g. `neondb` or `postgres`)
   * **Data Connectivity Mode:** Select **Import** (highly recommended for faster visuals and calculated measures).
4. Click **OK**.
5. Select the **Database** tab in the credentials prompt and input:
   * **User name:** `<CLOUD_USER>`
   * **Password:** `<CLOUD_PASSWORD>`
6. Click **Connect**.
7. In the Navigator window, check `fact_sales`, `dim_customers`, `dim_products`, `dim_shipping`, `dim_payments`, and `dim_dates`. Click **Load**.

---

## 🌍 Step 6: Configure Power BI Web Service Refresh

To publish your report to **Power BI Service** on the web and configure auto-refresh, you must handle the security firewall.

> [!WARNING]
> **Firewall & Security Rules:**
> * **Supabase/Neon:** They allow all public connections by default, protected by strong passwords. You can connect directly in the Power BI Service without installing an On-Premises Data Gateway.
> * **AWS RDS / Custom VMs:** You must modify your PostgreSQL security groups:
>   * Enable **"Public Access"** in AWS.
>   * Add a security rule whitelisting **Microsoft Azure IP ranges** to allow Power BI Cloud Refresh to bypass your firewall.
>   * Alternatively, configure an **On-Premises Data Gateway** running on an active VM or workstation.
