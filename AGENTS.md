# AGENTS.md - Marketing Intelligence Platform

## Project role

This repository contains the Marketing Intelligence Platform.

The Streamlit app is a BI/dashboard layer.
The backend ETL pipeline prepares marketing.db and the master_data table.

## Important paths

- main.py - backend pipeline entrypoint
- dashboard/app.py - Streamlit dashboard entrypoint
- src/etl/extract.py - raw CSV loading
- src/etl/transform.py - analytical dataset construction
- src/etl/load.py - SQLite loading
- src/analytics/kpi.py - KPI definitions
- requirements.txt - deployed dependency pins
- .streamlit/config.toml - Streamlit Cloud/runtime config

## Environment rules

Do not use plain python in this repository.

Use this for Python checks:

    conda run -n marketing-intel python
JUse this for Streamlit:

    conda run -n marketing-intel streamlit run dashboard/app.py

## Do-not-touch rules

Do not rebuild the dashboard from scratch.

Do not delete:
- KPI cards
- real KPI sparklines
- charts after KPI cards
- simple chart explanation/conclusion cards
- sidebar filters
- navigation
- 3D Lab
- deployment files

Do not change KPI formulas unless the user explicitly requests it.

Do not change data loading, table grain, joins, or filter behavior unless the task is specifically about data logic.

Do not commit, push, install packages, delete files, or rewrite large sections without explicit user approval.

## Data contract

master_data is expected to be one row per order_id.

Payments and items should remain aggregated before merging.

payment_value means Gross Payment Value unless filtered to delivered orders.

Delivered Revenue is based on payment_value where order_status == delivered.

## Safe verification commands

Run these after relevant edits:

    git status --short
    conda run -n marketing-intel python --version
    conda run -n marketing-intel python -c "import pandas, streamlit, sqlqlchemy, plotly; print('imports ok')"
    conda run -n marketing-intel python -m py_compile dashboard/app.py

For database checks:

    conda run -n marketing-intel python -c "import sqlite3; con=sqlite3.connect('marketing.db'); cur=con.cursor(); rows, orders = cur.execute('select count(*), count(distinct order_id) from master_data').fetchone(); print('rows:', rows, 'distinct_orders:', orders, 'ok:', rows == orders); con.close()"

For tests:

    conda run -n marketing-intel python -m pytest -p no:cacheprovider

## Workflow

Before editing:
1. Inspect files.
2. Explain findings.
3. Propose a small patch plan.
4. Wait for approval.

After editing:
1. Summarize changed files.
2. Run safe verification.
3. Show git status --short.
4. Do not commit or push unless explicitly approved.

## Preferred behavior

Be conservative.
Patch only the requested section.
Preserve accepted portfolio/dashboard work.
Prefer small diffs over rewrites.
