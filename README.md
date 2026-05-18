# 📊 Marketing Intelligence Platform

![CI Status](https://github.com/RuturajM31/marketing-intelligence-platform/actions/workflows/ci.yml/badge.svg)


An end-to-end **Data Engineering + Analytics + Machine Learning platform** built using Python.

This project simulates a real-world **e-commerce analytics system** using the Olist Brazilian dataset.

---
## 👨‍💻 Authors

- **Ruturaj Mokashi**
- **Nathanael Matutis**

---

# 🚀 Project Objective

To build a scalable analytics system that:
- Extracts and processes raw e-commerce data
- Builds a unified analytical dataset (ETL pipeline)
- Calculates business KPIs
- Performs customer segmentation
- Detects anomalies
- Generates business insights
- Validates pipeline using unit tests

---

# The Olist dataset contains multiple relational tables.

| Dataset        | Purpose                   |
| -------------- | ------------------------- |
| customers      | Customer information      |
| orders         | Order lifecycle           |
| order_items    | Product-level sales       |
| order_payments | Revenue/payment analysis  |
| order_reviews  | Customer satisfaction     |
| products       | Product category analysis |
| sellers        | Seller performance        |
| geolocation    | Regional analysis         |


---

## 📁 Project Structure

marketing-intelligence-platform/
│
├── src/
│   ├── config.py
│   ├── etl/
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── load.py
│   │   ├── download_data.py
│   │
│   ├── services/
│   │   ├── api_client.py
│   │   ├── data_quality.py
│   │
│   ├── analytics/
│   │   ├── kpi.py
│   │   ├── anomaly.py
│   │   ├── segmentation.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── schema.sql
│
├── dashboard/
│   ├── app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── tests/
│   ├── test_kpi.py
│
├── main.py

---

## 🚀 Problem Statement

Modern e-commerce platforms generate large volumes of data but struggle with:

- Identifying revenue drivers
- Understanding customer behavior
- Detecting inefficiencies in operations
- Tracking high-value customers
- Evaluating seller performance

---

## 💡 Solution Overview

This platform converts raw transactional data into **business-ready insights** using:

- ETL pipeline
- Centralized SQLite data warehouse
- KPI computation engine
- Machine learning models
- Automated reporting system
- CI/CD integration

---

## 🧠 Data Pipeline Flow

1. **Data Ingestion**
   - Kaggle API used for dataset download
   - Raw CSV files stored locally

2. **Data Transformation**
   - Joins across multiple tables
   - Creation of unified analytics dataset

3. **Data Storage**
   - Cleaned data loaded into SQLite warehouse

4. **Analytics Layer**
   - Revenue, AOV, order trends
   - Operational KPIs

5. **Machine Learning**
   - Customer segmentation (KMeans)
   - Anomaly detection (Isolation Forest)

6. **Reporting**
   - Matplotlib-based visualizations
   - Business dashboards

7. **Testing & CI/CD**
   - Pytest-based unit tests
   - GitHub Actions automation

---

## 📊 Key Business Insights

### 💰 Revenue Insights
- Total revenue: **~20.4M**
- High revenue concentration in top product categories (~70–80%)
- Strong daily fluctuations in sales patterns

### 🧍 Customer Insights
- ~70–80% are one-time buyers
- Repeat customers contribute disproportionately higher revenue
- Strong opportunity for retention optimization

### 🚚 Logistics Insights
- Late delivery rate: **~20–25%**
- Severe outliers in delivery delays
- Logistics inconsistency impacts customer satisfaction

### 🏪 Seller Insights
- Revenue highly concentrated among top sellers
- Significant performance imbalance across sellers

---

## 🤖 Machine Learning Models

### 🔹 Customer Segmentation (KMeans)
Segments customers based on:

- Recency
- Frequency
- Monetary value

**Output segments:**
- VIP Customers
- High Value Customers
- Mid Value Customers
- Low Value Customers

---

### 🔹 Anomaly Detection (Isolation Forest)

Detects:

- Unusual transaction patterns
- Extreme order values
- Behavioral outliers

---

## 📈 Visualizations

The system generates automated business insights:

- Revenue trends (daily & monthly)
- Customer segmentation distribution
- Delivery delay analysis
- Seller performance comparison

---

## 🧪 Testing Strategy

Robust testing ensures pipeline reliability:

- KPI validation tests
- ETL pipeline integrity checks
- ML output verification
- Data quality validation

---

## ⚙️ CI/CD Pipeline

Implemented using **GitHub Actions**:

On every push / pull request:

- Install dependencies
- Run unit tests
- Validate pipeline integrity

---

## 🛠️ Tech Stack

- Python 🐍
- Pandas / NumPy
- Scikit-learn
- Matplotlib
- SQLite
- Pytest
- GitHub Actions

---

## 🚀 Future Enhancements

- 📊 Power BI / Tableau integration
- ⚡ Apache Airflow orchestration
- ☁️ Cloud deployment (AWS / GCP)
- 🐳 Docker containerization
- 🔮 Forecasting models (Prophet / ARIMA)

---

## 🏁 Final Outcome

This project demonstrates:

- End-to-end data engineering pipeline
- Production-style analytics architecture
- Machine learning integration
- Automated testing & CI/CD
- Real-world business intelligence system design

---

## ⭐ Summary

A production-style **Marketing Intelligence Platform** that transforms raw e-commerce data into actionable business insights for decision-making.