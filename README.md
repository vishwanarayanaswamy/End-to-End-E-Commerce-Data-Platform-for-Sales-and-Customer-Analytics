<div align="center">

# 🛒 End-to-End E-Commerce Data Platform

### Sales & Customer Analytics — Data Engineering Capstone Project

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Airflow](https://img.shields.io/badge/Orchestration-Apache%20Airflow-017CEE?style=flat-square&logo=apacheairflow&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Dashboard-Power%20BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

</div>

---

### 👥 Team

| | Name | Focus |
|---|---|---|
| 🧹 | **Vishwa Narayanaswamy** | Raw data ingestion, cleaning, data quality framework , Power BI|
| 🔧 | **Koushik Raj Singh** | Airflow orchestration, Docker deployment, warehouse design, SQL analytics|

---

## 📖 What This Project Does

> Online stores generate a constant stream of messy data — customer records, orders, payments, shipping info — scattered across formats. Doing anything useful with it usually means someone cleaning spreadsheets by hand, over and over.

This project automates that entire pipeline, end to end:

```
📥 Ingest  →  🧹 Clean & Validate  →  🗄️ Load into Warehouse  →  📊 Analyze in Power BI
```

| Stage | What happens |
|---|---|
| 📥 **Ingest** | Raw e-commerce data comes in as files |
| 🧹 **Clean & validate** | Bad records (missing IDs, negative prices, impossible dates) are caught and quarantined automatically |
| 🗄️ **Load** | Clean data lands in a PostgreSQL warehouse, organized for fast queries |
| 📊 **Analyze** | A Power BI dashboard connects live and shows sales trends, customer retention, shipping performance |

Everything runs in Docker — one command starts the whole stack.

---

## 🗂️ What's In This Repo

### ⚙️ The Platform

| Path | Purpose |
|---|---|
| 🌬️ `dags/` | Airflow workflow that runs the pipeline steps in order, with retries |
| 🐍 `src/processing/etl.py` | Cleans and loads the data |
| 🗃️ `src/database/schema.sql` | Database tables and relationships |
| 📈 `src/database/analytics_queries.sql` | Ready-made SQL for sales/customer analytics |
| ✅ `src/tests/` | Automated checks that data quality rules are working |
| 🐳 `docker/postgres/` | Sets up the database when containers start |
| 🚧 `data/quarantine/` | Where bad records land instead of silently breaking things |
| 🐙 `docker-compose.yml` | Starts every service together |
| 📦 `requirements.txt` | Python dependencies |
| 🔐 `.env.example` | Template for local credentials — copy to `.env` and fill in |

### 📑 Supporting Materials

| File | For |
|---|---|
| 📄 `Data Engineering Project.pdf` | Full project write-up |
| 📝 `implementation_plan.md` | Planning notes |
| 📓 `PHASE 1-3.ipynb` | Notebook version of early cleaning/exploration |
| 🖼️ `data ingestion architecture.png` / `e commerce data flow.png` / `schema daigram.jpeg` | Architecture & schema diagrams |
| 📊 `End-to-End E-Commerce Data Platform Dashbord.pbix.zip` | Power BI dashboard file |
| 🔗 `POWER BI LINK.pdf` | Link to the hosted dashboard |
| 🖥️ `End-to-End-E-Commerce-Data-Platform (1).pptx` | Presentation slides |
| 🧾 `retail.csv` / `cleaned_retail_data.csv` / `Online_Retail_II_Cleaned (1) (1).xlsx` | Raw & cleaned datasets |

> ### ⚠️ Security note
> A `.env` file is committed in this repo alongside `.env.example`. `.env` files usually hold real passwords — confirm this one doesn't, then add `.env` to `.gitignore` so it's never committed again. Only `.env.example` (placeholder values) should be tracked.

---

## 🚀 Running It Locally

**1. Prerequisites**
- 🐳 [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Compose)
- 🐍 [Python 3.10+](https://www.python.org/downloads/) — only needed if running the ETL script outside Docker

**2. Set up your environment file**
```bash
cp .env.example .env
```
Fill in real values — don't reuse anything from the committed `.env`.

**3. Start everything**
```bash
docker compose up -d
```

**4. Load the schema and run the pipeline**
```bash
psql -h localhost -d ecommerce_dw -f src/database/schema.sql
python3 src/processing/etl.py --input cleaned_retail_data.csv --user <your_db_user>
```

**5. Run the data quality tests**
```bash
pytest src/tests/
```

**6. View the dashboard**
Unzip and open `End-to-End E-Commerce Data Platform Dashbord.pbix.zip` in Power BI Desktop, or follow the link in `POWER BI LINK.pdf`.

---

## ✅ Data Quality Rules

- 🚫 No blank IDs (`CustomerID`, `StockCode`, `InvoiceNo`, `sale_date`)
- 🚫 No negative or zero prices/quantities
- 🚫 No transaction dates before 2020-01-01 or after today
- 🧯 Anything that fails lands in `data/quarantine/bad_records.csv` instead of corrupting the warehouse

---



*Built as a data engineering capstone project — automated ingestion to interactive analytics, containerized end to end.*

</div>
