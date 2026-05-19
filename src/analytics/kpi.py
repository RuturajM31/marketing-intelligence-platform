import logging

import pandas as pd

logger = logging.getLogger(__name__)


def validate_df(df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Checks whether required columns exist before KPI calculation.
    """

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def total_revenue(df: pd.DataFrame) -> float:
    """
    Total payment value.

    Safe because transform.py creates one row per order.
    """

    validate_df(df, ["payment_value"])

    return float(df["payment_value"].sum())


def delivered_revenue(df: pd.DataFrame) -> float:
    """
    Revenue from delivered orders only.
    """

    validate_df(df, ["payment_value", "order_status"])

    delivered = df[df["order_status"] == "delivered"]

    return float(delivered["payment_value"].sum())


def total_orders(df: pd.DataFrame) -> int:
    """
    Counts unique orders.
    """

    validate_df(df, ["order_id"])

    return int(df["order_id"].nunique())


def average_order_value(df: pd.DataFrame) -> float:
    """
    Average revenue per order.
    """

    revenue = total_revenue(df)
    orders = total_orders(df)

    return revenue / orders if orders > 0 else 0.0


def unique_customers(df: pd.DataFrame) -> int:
    """
    Counts real unique customers using customer_unique_id.
    """

    validate_df(df, ["customer_unique_id"])

    return int(df["customer_unique_id"].nunique())


def revenue_per_customer(df: pd.DataFrame) -> float:
    """
    Average revenue per real customer.
    """

    revenue = total_revenue(df)
    customers = unique_customers(df)

    return revenue / customers if customers > 0 else 0.0


def orders_per_customer(df: pd.DataFrame) -> float:
    """
    Average orders per real customer.
    """

    validate_df(df, ["customer_unique_id", "order_id"])

    customer_count = df["customer_unique_id"].nunique()
    order_count = df["order_id"].nunique()

    return order_count / customer_count if customer_count > 0 else 0.0


def repeat_customer_rate(df: pd.DataFrame) -> float:
    """
    Percentage of real customers who placed more than one order.
    """

    validate_df(df, ["customer_unique_id", "order_id"])

    customer_orders = df.groupby(
        "customer_unique_id"
    )["order_id"].nunique()

    repeat_customers = (customer_orders > 1).sum()
    total_customers = customer_orders.count()

    return (
        repeat_customers / total_customers * 100
        if total_customers > 0
        else 0.0
    )


def late_delivery_rate(df: pd.DataFrame) -> float:
    """
    Percentage of orders delivered later than estimated.
    """

    validate_df(df, ["is_late_delivery"])

    valid = df["is_late_delivery"].dropna()

    if len(valid) == 0:
        return 0.0

    return float(valid.mean() * 100)


def average_delivery_time(df: pd.DataFrame) -> float:
    """
    Average delivery time in days.
    """

    validate_df(df, ["delivery_time_days"])

    return float(df["delivery_time_days"].dropna().mean())


def monthly_sales(df: pd.DataFrame) -> pd.Series:
    """
    Monthly revenue trend.
    """

    validate_df(
        df,
        ["order_purchase_timestamp", "payment_value"]
    )

    temp = df.copy()

    temp["order_purchase_timestamp"] = pd.to_datetime(
        temp["order_purchase_timestamp"],
        errors="coerce"
    )

    temp = temp.dropna(subset=["order_purchase_timestamp"])

    temp["month"] = (
        temp["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    return temp.groupby("month")["payment_value"].sum()


def monthly_revenue_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Month-over-month revenue growth percentage.
    """

    monthly = monthly_sales(df).sort_index()

    growth = monthly.pct_change() * 100

    result = growth.reset_index()
    result.columns = ["month", "revenue_growth_pct"]

    return result


def monthly_order_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Month-over-month order growth percentage.
    """

    validate_df(
        df,
        ["order_purchase_timestamp", "order_id"]
    )

    temp = df.copy()

    temp["order_purchase_timestamp"] = pd.to_datetime(
        temp["order_purchase_timestamp"],
        errors="coerce"
    )

    temp = temp.dropna(subset=["order_purchase_timestamp"])

    temp["month"] = (
        temp["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly_orders = (
        temp.groupby("month")["order_id"]
        .nunique()
        .sort_index()
    )

    growth = monthly_orders.pct_change() * 100

    result = growth.reset_index()
    result.columns = ["month", "order_growth_pct"]

    return result


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Runs all core KPIs together.
    """

    logger.info("Calculating KPIs...")

    results = {
        "total_revenue": total_revenue(df),
        "delivered_revenue": delivered_revenue(df),
        "total_orders": total_orders(df),
        "average_order_value": average_order_value(df),
        "unique_customers": unique_customers(df),
        "revenue_per_customer": revenue_per_customer(df),
        "orders_per_customer": orders_per_customer(df),
        "repeat_customer_rate": repeat_customer_rate(df),
    }

    if "is_late_delivery" in df.columns:
        results["late_delivery_rate"] = late_delivery_rate(df)

    if "delivery_time_days" in df.columns:
        results["average_delivery_time"] = average_delivery_time(df)

    logger.info("KPI calculation completed.")

    return results