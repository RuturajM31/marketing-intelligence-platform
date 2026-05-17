# 📊 Marketing Intelligence Platform

![CI Status](https://github.com/RuturajM31/marketing-intelligence-platform/actions/workflows/ci.yml/badge.svg)

> A production-style **end-to-end Data Engineering + Analytics + Machine Learning system** that transforms raw e-commerce data into actionable business intelligence.

---

## 👨‍💻 Authors

- **Ruturaj Mokashi**
- **Nathanael Matutis**

---

## 🎯 Problem Statement

Modern e-commerce companies generate massive amounts of data but struggle to:

- Understand revenue drivers
- Track customer behavior
- Detect operational inefficiencies
- Identify high-value customers
- Monitor seller performance

👉 This project solves these problems using a complete analytics pipeline.

---

## 🚀 Solution Overview

This system converts raw transactional data into **business-ready insights** using:

✔ ETL pipeline  
✔ Data warehouse (SQLite)  
✔ KPI engine  
✔ Machine learning models  
✔ Automated reporting  
✔ CI/CD pipeline  

---

## 🏗️ Architecture

```text
        ┌──────────────┐
        │  Raw Data     │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │   ETL Layer   │
        │ extract/transform/load │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │  Data Store   │ (SQLite)
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Analytics     │
        │ KPI + ML      │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Reporting     │
        │ Visualizations│
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ CI/CD Pipeline│
        └──────────────┘


---

## ⚙️ How the Project Was Built (Step-by-Step)

### 1️⃣ Data Ingestion (ETL Layer)
- Dataset downloaded using Kaggle API
- Raw CSV files stored locally
- Structured into DataFrames

### 2️⃣ Data Transformation
- Merged multiple tables:
  - Orders
  - Payments
  - Customers
  - Products
  - Sellers
- Built a unified **analytics-ready dataset**

### 3️⃣ Database Layer
- Loaded cleaned data into **SQLite**
- Enabled query-ready analytics environment

### 4️⃣ Analytics Engine
- KPI calculations (Revenue, Orders, AOV)
- Time-series revenue trends
- Operational metrics

### 5️⃣ Machine Learning Layer
- Customer segmentation using **KMeans**
- Anomaly detection using **Isolation Forest**

### 6️⃣ Reporting Layer
- Automated charts using Matplotlib
- Business dashboards:
  - Revenue trends
  - Customer behavior
  - Delivery delays
  - Seller performance

### 7️⃣ Testing & CI/CD
- Unit tests using **pytest**
- GitHub Actions for CI pipeline
- Automated validation on every push

---

## 📊 Key Business Insights

### 💰 Revenue Insights
- Total revenue: **~20.4M**
- Revenue is highly concentrated in top categories (~70–80%)
- Strong daily volatility in sales performance

---

### 🧍 Customer Insights
- ~70–80% customers are one-time buyers
- Repeat customers contribute significantly higher revenue
- Clear opportunity for retention optimization

---

### 🚚 Delivery Performance
- Late delivery rate: **~20–25%**
- Extreme delays exist in top 1% cases
- Logistics inconsistency affects customer experience

---

### 🏪 Seller Performance
- Top sellers contribute disproportionate revenue share
- High imbalance in seller ecosystem
- Performance optimization opportunity exists

---

## 🤖 Machine Learning Models

### 🔹 Customer Segmentation (KMeans)
Segments customers based on:
- Recency
- Frequency
- Monetary value

Output:
- VIP Customers
- High Value
- Mid Value
- Low Value

---

### 🔹 Anomaly Detection (Isolation Forest)
Detects:
- Unusual transactions
- Extreme order values
- Outlier customer behavior

---

## 📈 Sample Visualizations

### Revenue Trend
```

📈 Daily & Monthly Revenue Tracking
Helps identify seasonality and spikes


🧍 Customer segmentation & purchasing behavior
Identifies high-value vs low-value customers


🚚 Delivery delay distribution
Highlights operational inefficiencies


🧪 Testing Strategy

This project includes structured unit testing:

✔ KPI validation
✔ ETL correctness
✔ ML model outputs
✔ Data quality checks

🔄 CI/CD Pipeline

Automated workflow using GitHub Actions:

✔ Install dependencies
✔ Run unit tests
✔ Validate code quality

Triggered on:

Push to main
Pull requests

🛠 Tech Stack

Python
Pandas
NumPy
Scikit-learn
Matplotlib / Seaborn
SQLite
Pytest
GitHub Actions

📁 Project Structure

src/
 ├── etl/          # Data ingestion & transformation
 ├── analytics/    # KPI + ML models
 ├── reporting/    # Visualizations
 ├── db/           # Database layer
tests/             # Unit tests
main.py            # Pipeline entry point


🚀 Future Enhancements

📊 Power BI / Tableau dashboard integration
⚡ Apache Airflow orchestration
☁️ Cloud deployment (AWS / GCP)
📦 Docker containerization
🔮 Forecasting models (Prophet / ARIMA)

🏁 Final Impact

This project demonstrates:

✔ End-to-end data engineering pipeline
✔ Real-world analytics system design
✔ Machine learning integration
✔ Production-ready testing & CI/CD
✔ Business intelligence thinking

⭐ Outcome

A production-style Marketing Intelligence Platform that transforms raw data into actionable business decisions.