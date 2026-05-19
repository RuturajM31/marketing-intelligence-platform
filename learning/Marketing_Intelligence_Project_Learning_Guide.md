---
title: "Marketing Intelligence Platform - Learning Guide"
subtitle: "Simple explanation of the project, commands, file structure, methods, KPIs, debugging, and Git workflow"
author: "Prepared for Ruturaj Mokashi"
date: "2026-05-19"
toc: true
toc-depth: 3
numbersections: true
geometry: margin=0.75in
fontsize: 10.5pt
colorlinks: true
linkcolor: blue
urlcolor: blue
---

# Purpose of this Document

This document explains the full project in simple words.

It is not just a README. It is a learning guide for understanding how the project works, how the files talk to each other, how the pipeline runs, how KPIs are calculated, how to use Streamlit, how to debug problems, and how to avoid common mistakes.

The project is called:

```text
marketing-intelligence-platform
```

The project uses the Brazilian E-Commerce Public Dataset by Olist and builds a professional analytics workflow:

```text
Raw Kaggle CSV files
    -> ETL pipeline
    -> clean order-level master dataset
    -> data quality validation
    -> SQLite database
    -> KPIs, segmentation, anomaly detection
    -> reports, charts, Streamlit dashboard
```

# The Big Picture

Think of the project as two systems:

```text
SYSTEM 1: Backend data pipeline
--------------------------------
Runs with: python main.py

It downloads data, reads CSV files, transforms data,
validates it, loads it to SQLite, and generates reports.

SYSTEM 2: Frontend BI dashboard
-------------------------------
Runs with: streamlit run dashboard/app.py

It reads the clean SQLite table and shows interactive charts,
filters, and KPI cards.
```

The dashboard does not replace the ETL pipeline. The dashboard sits on top of the data pipeline.

## Visual Architecture

```text
+-----------------------------+
| Kaggle Olist Dataset        |
| Raw CSV files               |
+-------------+---------------+
              |
              v
+-----------------------------+
| src/etl/extract.py          |
| Read raw CSV files          |
+-------------+---------------+
              |
              v
+-----------------------------+
| src/etl/transform.py        |
| Build one-row-per-order     |
| master dataset              |
+-------------+---------------+
              |
              v
+-----------------------------+
| src/services/data_quality.py|
| Validate required columns   |
| Check missing/duplicates    |
+-------------+---------------+
              |
              v
+-----------------------------+
| src/etl/load.py             |
| Load to SQLite              |
| marketing.db/master_data    |
+-------------+---------------+
              |
              v
+-----------------------------+
| Analytics and Reporting     |
| KPIs, ML, CSVs, charts      |
+-------------+---------------+
              |
              v
+-----------------------------+
| dashboard/app.py            |
| Streamlit BI dashboard      |
+-----------------------------+
```

# Project Structure Explained

Your project folder currently looks like this:

```text
marketing-intelligence-platform/
|
|-- .github/
|   |-- workflows/
|       |-- ci.yml
|
|-- .streamlit/
|   |-- config.toml
|
|-- dashboard/
|   |-- app.py
|
|-- data/
|   |-- raw/
|   |-- processed/
|
|-- notebooks/
|
|-- src/
|   |-- config.py
|   |
|   |-- etl/
|   |   |-- download_data.py
|   |   |-- extract.py
|   |   |-- transform.py
|   |   |-- load.py
|   |
|   |-- services/
|   |   |-- api_client.py
|   |   |-- data_quality.py
|   |
|   |-- analytics/
|   |   |-- kpi.py
|   |   |-- segmentation.py
|   |   |-- anomaly.py
|   |
|   |-- reporting/
|   |   |-- export_charts.py
|   |   |-- generate_reports.py
|   |
|   |-- db/
|       |-- database.py
|       |-- schema.sql
|
|-- tests/
|   |-- test_kpi.py
|   |-- test_transform.py
|   |-- test_data_quality.py
|   |-- test_segmentation.py
|   |-- test_anomaly.py
|
|-- main.py
|-- requirements.txt
|-- requirements-dashboard.txt
|-- pytest.ini
|-- .gitignore
|-- README.md
|-- LICENSE
```

## What Each Important File Means

| File or Folder | Meaning |
|---|---|
| `main.py` | The main pipeline runner. This starts the backend workflow. |
| `src/config.py` | Stores important paths like `data/raw`, `data/processed`, and `marketing.db`. |
| `src/etl/download_data.py` | Downloads the Kaggle dataset using KaggleHub. |
| `src/etl/extract.py` | Reads raw CSV files into pandas DataFrames. |
| `src/etl/transform.py` | The most important ETL file. It creates the order-level master dataset. |
| `src/etl/load.py` | Saves the final DataFrame into SQLite. |
| `src/services/data_quality.py` | Checks required columns, missing values, duplicates, and empty data. |
| `src/analytics/kpi.py` | Calculates business KPIs like revenue, orders, repeat rate, AOV. |
| `src/analytics/segmentation.py` | Creates customer segments using KMeans. |
| `src/analytics/anomaly.py` | Detects unusual payments, deliveries, and sellers. |
| `src/reporting/generate_reports.py` | Calls KPI, segmentation, anomaly, and chart generation. |
| `src/reporting/export_charts.py` | Creates static chart images. |
| `dashboard/app.py` | Streamlit dashboard frontend. |
| `tests/` | Unit tests to check that the project logic works. |
| `requirements.txt` | Packages for the main ETL environment. |
| `requirements-dashboard.txt` | Packages for Streamlit dashboard environment. |
| `.gitignore` | Tells Git what not to track, such as virtual environments and data files. |

# Why We Use Two Python Environments

You have two virtual environments:

```text
venv
```

and:

```text
dashboard-venv
```

This is intentional.

## Main Environment: `venv`

Use this for:

```text
ETL pipeline
KPI calculations
ML modules
reports
unit tests
SQLite database creation
```

Run with:

```bash
source venv/bin/activate
python main.py
pytest -v
deactivate
```

## Dashboard Environment: `dashboard-venv`

Use this for:

```text
Streamlit dashboard
Plotly charts
frontend UI
```

Run with:

```bash
source dashboard-venv/bin/activate
streamlit run dashboard/app.py
```

## Why Not Put Everything in One Environment?

Streamlit often installs `pyarrow`. On your Mac, `pyarrow` caused build and segmentation problems. To protect the main pipeline, we separated dashboard dependencies from the ETL dependencies.

Simple rule:

```text
venv             -> backend pipeline
dashboard-venv   -> dashboard only
```

# Essential Commands

## Main Pipeline Test

Use this after changing backend files such as:

```text
main.py
src/etl/*.py
src/analytics/*.py
src/services/*.py
src/reporting/*.py
```

Command:

```bash
source venv/bin/activate
python main.py
pytest -v
deactivate
```

Meaning:

| Command | Meaning |
|---|---|
| `source venv/bin/activate` | Enter the main project environment. |
| `python main.py` | Run the complete backend ETL pipeline. |
| `pytest -v` | Run tests in verbose mode. |
| `deactivate` | Leave the environment. |

## Dashboard Test

Use this after changing:

```text
dashboard/app.py
.streamlit/config.toml
requirements-dashboard.txt
```

Command:

```bash
source dashboard-venv/bin/activate
streamlit run dashboard/app.py
```

Meaning:

| Command | Meaning |
|---|---|
| `source dashboard-venv/bin/activate` | Enter the dashboard environment. |
| `streamlit run dashboard/app.py` | Start the local dashboard. |

## After Changes in `app.py`

After replacing or editing `dashboard/app.py`, restart Streamlit:

```text
Ctrl + C
```

Then run:

```bash
streamlit cache clear
streamlit run dashboard/app.py
```

Meaning:

| Command | Meaning |
|---|---|
| `Ctrl + C` | Stop the running Streamlit server. |
| `streamlit cache clear` | Clear cached data so Streamlit reloads fresh logic. |
| `streamlit run dashboard/app.py` | Start dashboard again. |

# How `main.py` Runs the Project

`main.py` is the orchestrator. It does not do all the work itself. It calls functions from other files.

The flow is:

```text
main.py
  |
  |-- raw_data_available()
  |
  |-- download_dataset()          if raw files are missing
  |
  |-- extract_all_data()
  |
  |-- create_master_dataset(data)
  |
  |-- validate_data(master_df)
  |
  |-- load_to_db(master_df, "master_data")
  |
  |-- generate_report(master_df)
```

## Function Call Tree

```text
main()
|
|-- raw_data_available()
|     checks if data/raw has CSV files
|
|-- download_dataset()
|     downloads Kaggle files only if needed
|
|-- extract_all_data()
|     loads CSVs into DataFrames
|
|-- create_master_dataset(data)
|     builds clean order-level master DataFrame
|
|-- validate_data(master_df)
|     checks required columns and data quality
|
|-- load_to_db(master_df, "master_data")
|     saves data into marketing.db
|
|-- generate_report(master_df)
      |
      |-- calculate_kpis(master_df)
      |-- monthly_sales(master_df)
      |-- customer_segmentation(master_df)
      |-- run_all_anomaly_detection(master_df)
      |-- create_charts(master_df)
```

# The Most Important Concept: Data Grain

Before joining tables, always ask:

```text
What does one row represent?
```

This is called the grain of a table.

## Olist Table Grain

| Table | One row represents |
|---|---|
| `orders` | one order |
| `customers` | one customer/order record |
| `payments` | one payment row for an order |
| `items` | one product item row in an order |
| `products` | one product |
| `sellers` | one seller |
| `reviews` | one review |

The final master table should be:

```text
one row = one order
```

# The Big Mistake We Fixed: Many-to-Many Row Explosion

Imagine one order:

```text
order_id = O1
```

The order has 2 payment rows:

| order_id | payment_type | payment_value |
|---|---|---:|
| O1 | credit_card | 100 |
| O1 | voucher | 20 |

The same order has 3 item rows:

| order_id | product_id | price |
|---|---|---:|
| O1 | P1 | 50 |
| O1 | P2 | 40 |
| O1 | P3 | 30 |

If we merge raw payments and raw items directly:

```python
orders.merge(payments, on="order_id").merge(items, on="order_id")
```

Pandas creates:

```text
2 payment rows x 3 item rows = 6 rows
```

That is wrong.

Revenue becomes:

```text
100 + 100 + 100 + 20 + 20 + 20 = 360
```

But true revenue is:

```text
100 + 20 = 120
```

## Correct Fix

First aggregate payments:

```text
O1 -> payment_value = 120
```

Then aggregate items:

```text
O1 -> item_count = 3, total_item_price = 120
```

Then merge.

Correct final row:

| order_id | payment_value | item_count | total_item_price |
|---|---:|---:|---:|
| O1 | 120 | 3 | 120 |

# How `transform.py` Works

`transform.py` creates the final master dataset.

Simplified logic:

```text
1. Start with orders
2. Merge customers
3. Aggregate payments to one row per order
4. Merge aggregated payments
5. Add product/seller information to item rows
6. Aggregate items to one row per order
7. Merge aggregated items
8. Add reviews and geolocation if available
9. Convert date columns
10. Create delivery features
11. Fill safe numeric nulls
12. Check duplicate order_id rows
```

## Important Safety Check

At the end, the code checks:

```python
duplicate_orders = master["order_id"].duplicated().sum()
```

Expected:

```text
0
```

If the number is greater than zero, the code raises an error because the order-level grain is broken.

# How Data Quality Works

File:

```text
src/services/data_quality.py
```

This file protects the pipeline before loading and reporting.

## Main Function

```python
validate_data(df)
```

It checks:

```text
1. Is the DataFrame empty?
2. Are required columns present?
3. How many missing values are there?
4. How many duplicate rows are there?
```

Required columns usually include:

```text
order_id
customer_unique_id
payment_value
order_purchase_timestamp
```

## Why This Matters

If `payment_value` is missing, revenue calculation fails.

If `customer_unique_id` is missing, repeat customer rate fails.

If `order_purchase_timestamp` is missing, monthly sales fails.

This is better than letting the project fail later inside charts or KPIs.

# How KPIs Are Calculated

File:

```text
src/analytics/kpi.py
```

The main function is:

```python
calculate_kpis(df)
```

It calls smaller KPI functions.

## KPI Call Flow

```text
calculate_kpis(df)
|
|-- total_revenue(df)
|-- delivered_revenue(df)
|-- total_orders(df)
|-- average_order_value(df)
|-- unique_customers(df)
|-- revenue_per_customer(df)
|-- orders_per_customer(df)
|-- repeat_customer_rate(df)
|-- late_delivery_rate(df)
|-- average_delivery_time(df)
```

## Example 1: Total Revenue

Code idea:

```python
def total_revenue(df):
    return df["payment_value"].sum()
```

Simple meaning:

```text
Add all payment_value numbers.
```

Example:

| order_id | payment_value |
|---|---:|
| O1 | 100 |
| O2 | 200 |
| O3 | 300 |

Revenue:

```text
100 + 200 + 300 = 600
```

Because our master table is one row per order, this sum is safe.

## Example 2: Total Orders

Code idea:

```python
def total_orders(df):
    return df["order_id"].nunique()
```

Simple meaning:

```text
Count unique order_id values.
```

Example:

| order_id |
|---|
| O1 |
| O2 |
| O2 |
| O3 |

Unique orders:

```text
O1, O2, O3 = 3
```

## Example 3: Average Order Value

Formula:

```text
average_order_value = total_revenue / total_orders
```

Code idea:

```python
def average_order_value(df):
    revenue = total_revenue(df)
    orders = total_orders(df)
    return revenue / orders if orders > 0 else 0
```

Example:

```text
total_revenue = 600
total_orders = 3
AOV = 600 / 3 = 200
```

## Example 4: Unique Customers

The correct customer identifier is:

```text
customer_unique_id
```

Code idea:

```python
def unique_customers(df):
    return df["customer_unique_id"].nunique()
```

Do not use `customer_id` for repeat customer logic because it is order-specific in Olist.

## Example 5: Repeat Customer Rate

Code idea:

```python
customer_orders = df.groupby("customer_unique_id")["order_id"].nunique()
repeat_customers = (customer_orders > 1).sum()
total_customers = customer_orders.count()
rate = repeat_customers / total_customers * 100
```

Example:

| customer_unique_id | order_id |
|---|---|
| U1 | O1 |
| U1 | O2 |
| U2 | O3 |
| U3 | O4 |

Customer order counts:

| customer_unique_id | order_count |
|---|---:|
| U1 | 2 |
| U2 | 1 |
| U3 | 1 |

Repeat customers:

```text
U1 only = 1 repeat customer
```

Total customers:

```text
3
```

Repeat customer rate:

```text
1 / 3 * 100 = 33.33%
```

# How Reporting Works

File:

```text
src/reporting/generate_reports.py
```

This function:

```python
generate_report(df)
```

creates:

```text
kpis.csv
monthly_sales.csv
monthly_revenue_growth.csv
monthly_order_growth.csv
customer_segments.csv
payment_anomalies.csv
delivery_anomalies.csv
seller_anomalies.csv
charts/
```

It calls:

```text
calculate_kpis()
monthly_sales()
monthly_revenue_growth()
monthly_order_growth()
customer_segmentation()
run_all_anomaly_detection()
create_charts()
```

# How Customer Segmentation Works

File:

```text
src/analytics/segmentation.py
```

The idea is to group customers using RFM-style features:

| Feature | Meaning |
|---|---|
| Recency | How recently the customer purchased |
| Frequency | How many orders the customer placed |
| Monetary | How much the customer spent |

Simplified flow:

```text
1. Group data by customer_unique_id
2. Calculate recency, frequency, monetary
3. Scale the features
4. Apply KMeans clustering
5. Add a segment number
```

Simple example:

| customer | recency | frequency | monetary | likely segment |
|---|---:|---:|---:|---|
| U1 | 10 | 5 | 1000 | high value |
| U2 | 200 | 1 | 50 | low value |
| U3 | 30 | 2 | 300 | medium value |

# How Anomaly Detection Works

File:

```text
src/analytics/anomaly.py
```

The project uses Isolation Forest to find unusual patterns.

Examples of anomalies:

```text
very high payment value
extreme delivery delay
seller with unusual revenue/order behavior
```

Simple idea:

```text
Normal values are common.
Anomalies are rare and different from most values.
```

# How Streamlit Dashboard Works

File:

```text
dashboard/app.py
```

The dashboard reads from:

```text
marketing.db -> master_data
```

It does not read raw CSV files.

## Dashboard Flow

```text
dashboard/app.py
|
|-- load_master_data()
|     reads SQLite table
|
|-- prepare_data(df)
|     converts date columns
|
|-- apply_sidebar_filters(df)
|     filters by date, status, state, category
|
|-- show_kpi_cards(filtered_df)
|     shows KPI cards
|
|-- chart_monthly_revenue(filtered_df)
|-- chart_revenue_vs_orders(filtered_df)
|-- chart_customer_frequency(filtered_df)
|-- chart_customer_states(filtered_df)
|-- chart_order_status(filtered_df)
|-- chart_payment_methods(filtered_df)
|-- chart_delivery_delay(filtered_df)
|-- chart_top_categories(filtered_df)
|-- chart_top_sellers(filtered_df)
|-- show_data_quality(filtered_df)
```

## Why Dashboard Reads SQLite Instead of CSV

Bad approach:

```text
Streamlit reads raw CSVs and performs ETL every time.
```

Better approach:

```text
ETL creates clean master_data once.
Streamlit reads clean master_data.
```

This is more professional.

# Important Bash Commands

## Check Current Folder

```bash
pwd
```

## List Files

```bash
ls
```

## Activate Main Environment

```bash
source venv/bin/activate
```

## Activate Dashboard Environment

```bash
source dashboard-venv/bin/activate
```

## Leave an Environment

```bash
deactivate
```

## Check Which Python Is Active

```bash
which python
```

Expected for main environment:

```text
.../marketing-intelligence-platform/venv/bin/python
```

Expected for dashboard environment:

```text
.../marketing-intelligence-platform/dashboard-venv/bin/python
```

## Install Main Requirements

```bash
python -m pip install -r requirements.txt
```

## Install Dashboard Requirements

```bash
python -m pip install -r requirements-dashboard.txt
```

## Check Installed Packages

```bash
python -m pip list
```

# Important Git Commands

## Check Git Status

```bash
git status
```

Use this before every commit.

## Add Specific Files

```bash
git add dashboard/app.py .streamlit/config.toml README.md
```

This is safer than always using `git add .`.

## Commit

```bash
git commit -m "Polish Streamlit dashboard UI"
```

## Push

```bash
git push
```

## Full Safe Git Flow

```bash
git status
git add README.md dashboard/app.py .streamlit/config.toml
git commit -m "Update documentation and dashboard"
git push
git status
```

## What Not to Commit

Never commit:

```text
venv/
dashboard-venv/
venv_broken/
data/raw/
data/processed/
marketing.db
__pycache__/
.pytest_cache/
```

These are local or generated files.

# `.gitignore` Meaning

`.gitignore` tells Git which files/folders to ignore.

Important entries:

```gitignore
venv/
dashboard-venv/
venv_broken/
data/raw/
data/processed/
*.db
__pycache__/
.pytest_cache/
```

If VS Code shows thousands of files from `dashboard-venv`, check:

```bash
git check-ignore -v dashboard-venv/bin/python
```

Good output looks like:

```text
.gitignore:11:dashboard-venv/ dashboard-venv/bin/python
```

# Common Mistakes and Fixes

## Mistake 1: Running Terminal Commands Inside Python

If you see:

```text
>>>
```

you are inside Python.

Do not type:

```bash
python main.py
source venv/bin/activate
pip install pandas
```

inside `>>>`.

Exit Python:

```python
exit()
```

or press:

```text
Ctrl + D
```

Then run terminal commands in the shell.

## Mistake 2: Wrong Environment Active

Problem:

```text
ModuleNotFoundError: No module named 'pandas'
```

Cause:

```text
You are using an environment where pandas is not installed.
```

Fix:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Mistake 3: Thinking `requirements.txt` Runs Automatically

`requirements.txt` is only a list. Python does not read it automatically when you run `main.py`.

You must install it:

```bash
python -m pip install -r requirements.txt
```

## Mistake 4: Installing Streamlit in Main `venv`

This caused PyArrow problems.

Correct setup:

```text
requirements.txt             -> main ETL packages
requirements-dashboard.txt   -> Streamlit dashboard packages
```

## Mistake 5: Pushing Virtual Environments to GitHub

Bad:

```text
venv/
dashboard-venv/
venv_broken/
```

Good:

```text
requirements.txt
requirements-dashboard.txt
```

The requirements files are the recipe. The virtual environments are local installations.

## Mistake 6: Using `customer_id` for Repeat Customer Rate

Wrong:

```python
df.groupby("customer_id")["order_id"].nunique()
```

Better for Olist:

```python
df.groupby("customer_unique_id")["order_id"].nunique()
```

## Mistake 7: Merging Raw Payments and Items Directly

Wrong:

```python
orders.merge(payments, on="order_id").merge(items, on="order_id")
```

Better:

```text
aggregate payments by order_id
aggregate items by order_id
then merge
```

# Debugging Checklist

## Check Environment

```bash
which python
python -m pip list
```

## Check Imports

```bash
python -c "import pandas; import kagglehub; import sklearn; print('imports ok')"
```

## Check Main Pipeline

```bash
source venv/bin/activate
python main.py
```

## Check Tests

```bash
pytest -v
```

## Check SQLite Table

```bash
python -c "import pandas as pd; from sqlalchemy import create_engine; e=create_engine('sqlite:///marketing.db'); print(pd.read_sql('SELECT COUNT(*) AS rows FROM master_data', e))"
```

## Check Data Explosion

```bash
python
```

Then:

```python
from src.etl.extract import extract_all_data
from src.etl.transform import create_master_dataset

data = extract_all_data()
df = create_master_dataset(data)
df["order_id"].duplicated().sum()
```

Expected:

```text
0
```

# Professional Daily Workflow

## When You Change Backend Code

Backend files include:

```text
main.py
src/etl/*.py
src/services/*.py
src/analytics/*.py
src/reporting/*.py
```

Run:

```bash
source venv/bin/activate
python main.py
pytest -v
deactivate
```

## When You Change Dashboard Code

Dashboard files include:

```text
dashboard/app.py
.streamlit/config.toml
```

Run:

```bash
source dashboard-venv/bin/activate
streamlit cache clear
streamlit run dashboard/app.py
```

## When You Change Documentation

Run:

```bash
git status
git add README.md
git commit -m "Update documentation"
git push
```

# Mental Model to Remember

```text
Raw data is messy.
ETL makes it clean.
Validation checks if it is safe.
SQLite stores it.
Analytics calculates insights.
Streamlit displays insights.
Tests protect the logic.
Git tracks only source code, not local generated files.
```

# Final Submission Checklist

Before submitting or presenting the project:

```text
[ ] README.md is updated
[ ] requirements.txt does not include Streamlit/PyArrow
[ ] requirements-dashboard.txt contains dashboard packages
[ ] .gitignore ignores venv, dashboard-venv, data, db files
[ ] python main.py runs successfully
[ ] pytest -v passes
[ ] streamlit run dashboard/app.py works
[ ] GitHub repo does not show virtual environments
[ ] dashboard screenshots look professional
[ ] you can explain one-row-per-order grain
[ ] you can explain why customer_unique_id matters
[ ] you can explain why raw payments/items should not be merged directly
```

# Glossary

| Term | Simple Meaning |
|---|---|
| DataFrame | A table in pandas. |
| ETL | Extract, Transform, Load. |
| Grain | What one row represents. |
| KPI | Business metric, such as revenue or orders. |
| Merge | Joining two tables. |
| Aggregation | Grouping rows and summarizing them. |
| SQLite | Local database file. |
| Streamlit | Python framework for simple web dashboards. |
| Virtual environment | Isolated Python package environment. |
| pytest | Python testing framework. |
| Git | Version control system. |
| `.gitignore` | File that tells Git what not to track. |

# Best Explanation for Interviews or Project Submission

You can explain the project like this:

```text
This project is an end-to-end e-commerce analytics platform built with Python.
It downloads the Olist dataset, transforms multiple raw relational tables into a clean order-level analytical dataset, validates data quality, stores the curated data in SQLite, calculates business KPIs, performs customer segmentation and anomaly detection, and exposes the results through a Streamlit dashboard.

A key modeling decision was to keep the final master table at one row per order. Payments and order items are aggregated before joining to prevent many-to-many row explosion and inflated revenue. Customer analytics uses customer_unique_id to correctly identify repeat customers.
```

That explanation is professional and shows that you understand both Python and BI/data modeling.
