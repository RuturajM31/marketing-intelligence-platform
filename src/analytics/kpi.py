# ============================================================
# KPI ANALYTICS
# Marketing Intelligence Platform
# ============================================================

"""
This file contains KPI calculation functions.

KPI means Key Performance Indicator.

These functions are used by:

1. main.py
   - to calculate reports

2. dashboard/app.py
   - to show KPI cards in Streamlit

3. tests/
   - to verify KPI logic

Important business wording:
---------------------------
In the Olist dataset, canceled orders may still have payment_value.

So we separate:

Gross Payment Value
    = sum(payment_value) for selected orders, regardless of status

Delivered Revenue
    = sum(payment_value) only for delivered orders

This avoids the mistake of calling canceled order payments "real revenue".
"""

# logging lets us write useful messages when KPI calculation runs.
import logging

# pandas is used for dataframe operations.
import pandas as pd


# Create a logger for this file.
# __name__ means the logger name becomes src.analytics.kpi.
logger = logging.getLogger(__name__)


# ============================================================
# VALIDATION HELPER
# ============================================================

def validate_df(df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Checks whether required columns exist before KPI calculation.

    Why this matters:
        If a function needs payment_value but the dataframe does not have it,
        the error should be clear and easy to understand.

    Example:
        validate_df(df, ["payment_value", "order_id"])

    If one column is missing, this function raises ValueError.
    """

    # Create a list of required columns that are missing from df.
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    # If any required columns are missing, stop the function with a clear error.
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# ============================================================
# CORE FINANCIAL KPIS
# ============================================================

def total_revenue(df: pd.DataFrame) -> float:
    """
    Calculates Gross Payment Value.

    Original function name:
        total_revenue

    Business meaning:
        This is actually Gross Payment Value.

    Formula:
        sum(payment_value)

    Important:
        This includes selected orders regardless of order_status.
        Therefore, canceled orders may be included if they have payment_value.

    Why keep the name total_revenue?
        Your existing project and tests may already call this function.
        So we keep the old function name for compatibility.
    """

    # Check that payment_value exists.
    validate_df(df, ["payment_value"])

    # Sum payment_value and convert result to float.
    return float(df["payment_value"].sum())


def delivered_revenue(df: pd.DataFrame) -> float:
    """
    Calculates revenue from delivered orders only.

    Formula:
        sum(payment_value where order_status == "delivered")

    Why this matters:
        Delivered Revenue is closer to recognized/real business revenue.
        Canceled orders are not included here.
    """

    # Check that required columns exist.
    validate_df(df, ["payment_value", "order_status"])

    # Keep only delivered orders.
    delivered = df[df["order_status"] == "delivered"]

    # Sum payment_value for delivered orders only.
    return float(delivered["payment_value"].sum())


def canceled_gross_payment_value(df: pd.DataFrame) -> float:
    """
    Calculates gross payment value for canceled orders.

    Formula:
        sum(payment_value where order_status == "canceled")

    Why this matters:
        This explains why canceled orders can show payment value in the dashboard.
        It should not be treated as Delivered Revenue.
    """

    # Check that required columns exist.
    validate_df(df, ["payment_value", "order_status"])

    # Keep only canceled orders.
    canceled = df[df["order_status"] == "canceled"]

    # Sum payment value for canceled orders.
    return float(canceled["payment_value"].sum())


def total_orders(df: pd.DataFrame) -> int:
    """
    Counts unique orders.

    Formula:
        count distinct order_id

    Why unique?
        Even though our master dataset should be one row per order,
        using nunique() protects us from accidental duplicates.
    """

    # Check that order_id exists.
    validate_df(df, ["order_id"])

    # Count unique order IDs.
    return int(df["order_id"].nunique())


def average_order_value(df: pd.DataFrame) -> float:
    """
    Calculates Average Gross Order Value.

    Formula:
        Gross Payment Value / Total Orders

    Important:
        This is based on total_revenue(), which means Gross Payment Value.
    """

    # Calculate Gross Payment Value.
    revenue = total_revenue(df)

    # Calculate unique orders.
    orders = total_orders(df)

    # Avoid division by zero.
    return revenue / orders if orders > 0 else 0.0


def revenue_per_customer(df: pd.DataFrame) -> float:
    """
    Calculates average Gross Payment Value per customer.

    Formula:
        Gross Payment Value / Unique Customers
    """

    # Calculate Gross Payment Value.
    revenue = total_revenue(df)

    # Calculate unique customers.
    customers = unique_customers(df)

    # Avoid division by zero.
    return revenue / customers if customers > 0 else 0.0


# ============================================================
# CUSTOMER KPIS
# ============================================================

def unique_customers(df: pd.DataFrame) -> int:
    """
    Counts real unique customers using customer_unique_id.

    Why not customer_id?
        In the Olist dataset, customer_id is linked to a specific order.
        customer_unique_id identifies the real customer across multiple orders.
    """

    # Check that customer_unique_id exists.
    validate_df(df, ["customer_unique_id"])

    # Count unique real customers.
    return int(df["customer_unique_id"].nunique())


def orders_per_customer(df: pd.DataFrame) -> float:
    """
    Calculates average orders per customer.

    Formula:
        Total Orders / Unique Customers
    """

    # Check that required columns exist.
    validate_df(df, ["customer_unique_id", "order_id"])

    # Count unique customers.
    customer_count = df["customer_unique_id"].nunique()

    # Count unique orders.
    order_count = df["order_id"].nunique()

    # Avoid division by zero.
    return order_count / customer_count if customer_count > 0 else 0.0


def repeat_customer_rate(df: pd.DataFrame) -> float:
    """
    Calculates repeat customer rate.

    Formula:
        customers with more than 1 order / total customers * 100

    Why this matters:
        Shows whether customers come back after their first purchase.
    """

    # Check required columns.
    validate_df(df, ["customer_unique_id", "order_id"])

    # Count unique orders per customer.
    customer_orders = df.groupby(
        "customer_unique_id"
    )["order_id"].nunique()

    # Count customers with more than one order.
    repeat_customers = (customer_orders > 1).sum()

    # Count all customers in this grouped result.
    total_customers = customer_orders.count()

    # Convert to percentage.
    return (
        repeat_customers / total_customers * 100
        if total_customers > 0
        else 0.0
    )


# ============================================================
# ORDER STATUS / OPERATIONS KPIS
# ============================================================

def delivered_orders(df: pd.DataFrame) -> int:
    """
    Counts unique delivered orders.

    Formula:
        count distinct order_id where order_status == "delivered"
    """

    # Check required columns.
    validate_df(df, ["order_id", "order_status"])

    # Filter delivered orders and count unique order IDs.
    return int(
        df.loc[df["order_status"] == "delivered", "order_id"]
        .nunique()
    )


def canceled_orders(df: pd.DataFrame) -> int:
    """
    Counts unique canceled orders.

    Formula:
        count distinct order_id where order_status == "canceled"
    """

    # Check required columns.
    validate_df(df, ["order_id", "order_status"])

    # Filter canceled orders and count unique order IDs.
    return int(
        df.loc[df["order_status"] == "canceled", "order_id"]
        .nunique()
    )


def unavailable_orders(df: pd.DataFrame) -> int:
    """
    Counts unique unavailable orders.

    Formula:
        count distinct order_id where order_status == "unavailable"
    """

    # Check required columns.
    validate_df(df, ["order_id", "order_status"])

    # Filter unavailable orders and count unique order IDs.
    return int(
        df.loc[df["order_status"] == "unavailable", "order_id"]
        .nunique()
    )


def cancellation_rate(df: pd.DataFrame) -> float:
    """
    Calculates cancellation rate.

    Formula:
        Canceled Orders / Total Orders * 100

    Example:
        625 canceled orders / 99,441 total orders * 100
    """

    # Calculate total order count.
    orders = total_orders(df)

    # Avoid division by zero.
    if orders == 0:
        return 0.0

    # Calculate cancellation percentage.
    return canceled_orders(df) / orders * 100


def delivery_success_rate(df: pd.DataFrame) -> float:
    """
    Calculates delivery success rate.

    Formula:
        Delivered Orders / Total Orders * 100

    Why this matters:
        It shows what share of selected orders reached delivered status.
    """

    # Calculate total order count.
    orders = total_orders(df)

    # Avoid division by zero.
    if orders == 0:
        return 0.0

    # Calculate delivery success percentage.
    return delivered_orders(df) / orders * 100


# ============================================================
# DELIVERY KPIS
# ============================================================

def late_delivery_rate(df: pd.DataFrame) -> float:
    """
    Calculates percentage of late deliveries.

    Preferred input:
        is_late_delivery

    Backup input:
        delivery_delay_days

    Formula using is_late_delivery:
        mean(is_late_delivery) * 100

    Formula using delivery_delay_days:
        percentage of rows where delivery_delay_days > 0

    Meaning:
        If is_late_delivery is True/1, order was late.
        If delivery_delay_days > 0, order was late.

    Why this safer version is useful:
        If transform.py creates is_late_delivery, we use it.
        If that column is missing but delivery_delay_days exists, KPI still works.
    """

    # Best case: use is_late_delivery if it exists.
    if "is_late_delivery" in df.columns:

        # Remove missing values.
        valid = df["is_late_delivery"].dropna()

        # If no valid values exist, return 0.
        if len(valid) == 0:
            return 0.0

        # Boolean mean gives share of True values.
        return float(valid.mean() * 100)

    # Backup case: use delivery_delay_days if is_late_delivery does not exist.
    if "delivery_delay_days" in df.columns:

        # Remove missing values.
        valid = df["delivery_delay_days"].dropna()

        # If no valid values exist, return 0.
        if len(valid) == 0:
            return 0.0

        # Late delivery means delivery_delay_days is greater than 0.
        return float((valid > 0).mean() * 100)

    # If neither column exists, return 0 safely.
    return 0.0


def average_delivery_time(df: pd.DataFrame) -> float:
    """
    Calculates average delivery time in days.

    Input column:
        delivery_time_days

    Meaning:
        Average days from purchase to customer delivery.
    """

    # Check that delivery_time_days exists.
    validate_df(df, ["delivery_time_days"])

    # Calculate average after removing missing values.
    value = df["delivery_time_days"].dropna().mean()

    # If the result is NaN, return 0.
    return 0.0 if pd.isna(value) else float(value)


def average_review_score(df: pd.DataFrame) -> float:
    """
    Calculates average customer review score.

    Input column:
        review_score

    Why this matters:
        Connects customer satisfaction with delivery and operations.
    """

    # If review_score does not exist, return 0.
    if "review_score" not in df.columns:
        return 0.0

    # Calculate average review score.
    value = df["review_score"].dropna().mean()

    # If all values were missing, mean becomes NaN.
    return 0.0 if pd.isna(value) else float(value)


# ============================================================
# MONTHLY TIME-SERIES KPIS
# ============================================================

def monthly_sales(df: pd.DataFrame) -> pd.Series:
    """
    Calculates monthly Gross Payment Value.

    Output:
        pandas Series

    Index:
        month

    Values:
        sum(payment_value)
    """

    # Check required columns.
    validate_df(
        df,
        ["order_purchase_timestamp", "payment_value"]
    )

    # Work on a copy so original dataframe is not changed.
    temp = df.copy()

    # Convert order_purchase_timestamp to datetime.
    temp["order_purchase_timestamp"] = pd.to_datetime(
        temp["order_purchase_timestamp"],
        errors="coerce"
    )

    # Remove rows with invalid/missing purchase timestamp.
    temp = temp.dropna(subset=["order_purchase_timestamp"])

    # Create month column.
    # Example: 2017-05-12 becomes Period('2017-05', 'M')
    temp["month"] = (
        temp["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    # Group by month and sum payment values.
    return temp.groupby("month")["payment_value"].sum()


def monthly_revenue_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates month-over-month Gross Payment Value growth.

    Formula:
        (current month value - previous month value)
        / previous month value * 100

    Note:
        Function name says revenue for compatibility,
        but the business meaning is Gross Payment Value growth.
    """

    # Get monthly Gross Payment Value and sort by month.
    monthly = monthly_sales(df).sort_index()

    # Calculate percentage change from previous month.
    growth = monthly.pct_change() * 100

    # Convert Series to DataFrame.
    result = growth.reset_index()

    # Rename columns.
    result.columns = ["month", "revenue_growth_pct"]

    # Convert Period month to string so it is easier to export/display.
    result["month"] = result["month"].astype(str)

    # Return growth dataframe.
    return result


def monthly_order_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates month-over-month order growth.

    Formula:
        (current month orders - previous month orders)
        / previous month orders * 100
    """

    # Check required columns.
    validate_df(
        df,
        ["order_purchase_timestamp", "order_id"]
    )

    # Work on a copy.
    temp = df.copy()

    # Convert purchase timestamp to datetime.
    temp["order_purchase_timestamp"] = pd.to_datetime(
        temp["order_purchase_timestamp"],
        errors="coerce"
    )

    # Remove rows without valid date.
    temp = temp.dropna(subset=["order_purchase_timestamp"])

    # Create month column.
    temp["month"] = (
        temp["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    # Count unique orders per month.
    monthly_orders = (
        temp.groupby("month")["order_id"]
        .nunique()
        .sort_index()
    )

    # Calculate month-over-month percentage growth.
    growth = monthly_orders.pct_change() * 100

    # Convert Series to DataFrame.
    result = growth.reset_index()

    # Rename columns.
    result.columns = ["month", "order_growth_pct"]

    # Convert Period month to string.
    result["month"] = result["month"].astype(str)

    # Return order growth dataframe.
    return result


# ============================================================
# MAIN KPI DICTIONARY
# ============================================================

def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Runs all core KPIs together.

    Returns:
        dictionary of KPI names and values

    Example:
        {
            "total_revenue": 16010000,
            "delivered_revenue": 15420000,
            "canceled_orders": 625
        }

    Note:
        The key "total_revenue" is kept for compatibility.
        In the dashboard, we label it as "Gross Payment Value".
    """

    # Log start of KPI calculation.
    logger.info("Calculating KPIs...")

    # Calculate all KPIs.
    results = {
        # Kept old key name for compatibility with your existing code.
        # Dashboard should display this as Gross Payment Value.
        "total_revenue": total_revenue(df),

        # Delivered-only revenue.
        "delivered_revenue": delivered_revenue(df),

        # Order KPIs.
        "total_orders": total_orders(df),
        "average_order_value": average_order_value(df),

        # Customer KPIs.
        "unique_customers": unique_customers(df),
        "revenue_per_customer": revenue_per_customer(df),
        "orders_per_customer": orders_per_customer(df),
        "repeat_customer_rate": repeat_customer_rate(df),

        # Operational KPIs.
        "delivered_orders": delivered_orders(df),
        "canceled_orders": canceled_orders(df),
        "unavailable_orders": unavailable_orders(df),
        "cancellation_rate": cancellation_rate(df),
        "delivery_success_rate": delivery_success_rate(df),
        "canceled_gross_payment_value": canceled_gross_payment_value(df),

        # Delivery and review KPIs.
        "late_delivery_rate": late_delivery_rate(df),
        "average_review_score": average_review_score(df),
    }

    # Add average delivery time only if the column exists.
    # This keeps the function flexible for tests or partial datasets.
    if "delivery_time_days" in df.columns:
        results["average_delivery_time"] = average_delivery_time(df)
        results["average_delivery_time_days"] = average_delivery_time(df)
    else:
        results["average_delivery_time"] = 0.0
        results["average_delivery_time_days"] = 0.0

    # Log completion.
    logger.info("KPI calculation completed.")

    # Return dictionary to dashboard/reporting layer.
    return results