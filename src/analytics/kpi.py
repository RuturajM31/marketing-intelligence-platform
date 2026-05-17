# ============================================
# KPI ANALYTICS LAYER
# ============================================

# This file:
# - calculates business KPIs
# - tracks revenue performance
# - measures customer behavior
# - supports BI reporting

import pandas as pd
import logging

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ============================================
# VALIDATION FUNCTION
# ============================================

def validate_df(df, required_columns):
    """
    Validates whether required columns exist
    inside dataframe before KPI calculation
    """

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


# ============================================
# BASIC KPIs
# ============================================

# --------------------------------------------
# TOTAL REVENUE
# --------------------------------------------
def total_revenue(df):
    """
    Calculates total revenue
    """

    validate_df(df, ["payment_value"])

    revenue = df["payment_value"].sum()

    logger.info(f"Total Revenue calculated: {revenue}")

    return revenue


# --------------------------------------------
# TOTAL ORDERS
# --------------------------------------------
def total_orders(df):
    """
    Calculates total unique orders
    """

    validate_df(df, ["order_id"])

    orders = df["order_id"].nunique()

    logger.info(f"Total Orders calculated: {orders}")

    return orders


# --------------------------------------------
# AVERAGE ORDER VALUE
# --------------------------------------------
def average_order_value(df):
    """
    Calculates average revenue per order
    """

    validate_df(df, ["payment_value", "order_id"])

    revenue = df["payment_value"].sum()
    orders = df["order_id"].nunique()

    aov = revenue / orders if orders > 0 else 0

    logger.info(f"Average Order Value calculated: {aov}")

    return aov


# ============================================
# CUSTOMER KPIs
# ============================================

# --------------------------------------------
# UNIQUE CUSTOMERS
# --------------------------------------------
def unique_customers(df):
    """
    Number of unique customers
    """

    validate_df(df, ["customer_id"])

    value = df["customer_id"].nunique()

    logger.info(f"Unique Customers calculated: {value}")

    return value


# --------------------------------------------
# REVENUE PER CUSTOMER
# --------------------------------------------
def revenue_per_customer(df):
    """
    Average revenue generated per customer
    """

    validate_df(df, ["customer_id", "payment_value"])

    customers = df["customer_id"].nunique()
    revenue = df["payment_value"].sum()

    arpu = revenue / customers if customers > 0 else 0

    logger.info(f"Revenue per Customer calculated: {arpu}")

    return arpu


# --------------------------------------------
# ORDERS PER CUSTOMER
# --------------------------------------------
def orders_per_customer(df):
    """
    Average number of orders per customer
    """

    validate_df(df, ["customer_id", "order_id"])

    orders = df["order_id"].nunique()
    customers = df["customer_id"].nunique()

    opc = orders / customers if customers > 0 else 0

    logger.info(f"Orders per Customer calculated: {opc}")

    return opc


# --------------------------------------------
# REPEAT CUSTOMER RATE
# --------------------------------------------
def repeat_customer_rate(df):
    """
    Percentage of customers
    who placed more than 1 order
    """

    validate_df(df, ["customer_id", "order_id"])

    customer_orders = df.groupby(
        "customer_id"
    )["order_id"].nunique()

    repeat_customers = (
        customer_orders > 1
    ).sum()

    total_customers = customer_orders.count()

    rate = (
        repeat_customers / total_customers * 100
    ) if total_customers > 0 else 0

    logger.info(
        f"Repeat Customer Rate calculated: {rate}%"
    )

    return rate


# ============================================
# TIME-BASED KPIs
# ============================================

# --------------------------------------------
# MONTHLY SALES
# --------------------------------------------
def monthly_sales(df):
    """
    Monthly revenue trend
    """

    validate_df(
        df,
        ["order_purchase_timestamp", "payment_value"]
    )

    df = df.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly = df.groupby(
        "month"
    )["payment_value"].sum()

    logger.info("Monthly sales calculated")

    return monthly


# --------------------------------------------
# MONTHLY REVENUE GROWTH
# --------------------------------------------
def monthly_revenue_growth(df):
    """
    Month-over-month revenue growth %
    """

    validate_df(
        df,
        ["order_purchase_timestamp", "payment_value"]
    )

    df = df.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["order_purchase_timestamp"]
    )

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly = df.groupby(
        "month"
    )["payment_value"].sum().sort_index()

    growth = monthly.pct_change() * 100

    result = growth.reset_index()

    result.columns = [
        "month",
        "revenue_growth_pct"
    ]

    logger.info(
        "Monthly revenue growth calculated"
    )

    return result


# --------------------------------------------
# MONTHLY ORDER GROWTH
# --------------------------------------------
def monthly_order_growth(df):
    """
    Month-over-month order growth %
    """

    validate_df(
        df,
        ["order_purchase_timestamp", "order_id"]
    )

    df = df.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["order_purchase_timestamp"]
    )

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly = df.groupby(
        "month"
    )["order_id"].nunique().sort_index()

    growth = monthly.pct_change() * 100

    result = growth.reset_index()

    result.columns = [
        "month",
        "order_growth_pct"
    ]

    logger.info(
        "Monthly order growth calculated"
    )

    return result


# ============================================
# MASTER KPI FUNCTION
# ============================================

def calculate_kpis(df):
    """
    Runs all important KPI calculations
    """

    logger.info("Starting KPI calculations...")

    results = {

        # Revenue KPIs
        "total_revenue": total_revenue(df),
        "total_orders": total_orders(df),
        "average_order_value": average_order_value(df),

        # Customer KPIs
        "unique_customers": unique_customers(df),
        "revenue_per_customer": revenue_per_customer(df),
        "orders_per_customer": orders_per_customer(df),
        "repeat_customer_rate": repeat_customer_rate(df),
    }

    logger.info("All KPIs calculated successfully")

    return results