import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


def create_charts(df: pd.DataFrame) -> None:
    """
    Creates business charts and saves them to data/processed/charts.
    """

    chart_path = "data/processed/charts"

    os.makedirs(chart_path, exist_ok=True)

    temp = df.copy()

    if "order_purchase_timestamp" in temp.columns:
        temp["order_purchase_timestamp"] = pd.to_datetime(
            temp["order_purchase_timestamp"],
            errors="coerce"
        )

    if {
        "order_purchase_timestamp",
        "payment_value"
    }.issubset(temp.columns):

        daily_revenue = temp.dropna(
            subset=["order_purchase_timestamp"]
        ).groupby(
            temp["order_purchase_timestamp"].dt.date
        )["payment_value"].sum()

        plt.figure(figsize=(14, 6))
        daily_revenue.plot()
        plt.title("Daily Revenue Trend")
        plt.xlabel("Date")
        plt.ylabel("Revenue")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/daily_revenue_trend.png")
        plt.close()

    if {
        "order_purchase_timestamp",
        "payment_value"
    }.issubset(temp.columns):

        monthly_revenue = temp.dropna(
            subset=["order_purchase_timestamp"]
        ).groupby(
            temp["order_purchase_timestamp"].dt.to_period("M")
        )["payment_value"].sum()

        plt.figure(figsize=(14, 6))
        monthly_revenue.plot(kind="bar")
        plt.title("Monthly Revenue")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/monthly_revenue.png")
        plt.close()

    category_column = None

    if "main_product_category_english" in temp.columns:
        category_column = "main_product_category_english"
    elif "main_product_category" in temp.columns:
        category_column = "main_product_category"

    if category_column and "payment_value" in temp.columns:
        top_categories = (
            temp.groupby(category_column)["payment_value"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        plt.figure(figsize=(12, 7))
        top_categories.sort_values().plot(kind="barh")
        plt.title("Top 10 Product Categories by Revenue")
        plt.xlabel("Revenue")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/top_categories.png")
        plt.close()

    if {
        "customer_unique_id",
        "order_id"
    }.issubset(temp.columns):

        customer_orders = temp.groupby(
            "customer_unique_id"
        )["order_id"].nunique()

        plt.figure(figsize=(12, 6))
        sns.histplot(customer_orders, bins=30, kde=True)
        plt.title("Customer Order Frequency Distribution")
        plt.xlabel("Orders per Customer")
        plt.ylabel("Number of Customers")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/customer_frequency.png")
        plt.close()

    if "primary_payment_type" in temp.columns:
        payment_counts = temp["primary_payment_type"].value_counts()

        plt.figure(figsize=(8, 8))
        plt.pie(
            payment_counts,
            labels=payment_counts.index,
            autopct="%1.1f%%"
        )
        plt.title("Primary Payment Method Distribution")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/payment_methods.png")
        plt.close()

    if "order_status" in temp.columns:
        plt.figure(figsize=(12, 6))
        sns.countplot(data=temp, x="order_status")
        plt.title("Order Status Distribution")
        plt.xlabel("Order Status")
        plt.ylabel("Count")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig(f"{chart_path}/order_status.png")
        plt.close()

    if {
        "main_seller_id",
        "payment_value"
    }.issubset(temp.columns):

        seller_performance = (
            temp.groupby("main_seller_id")["payment_value"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        plt.figure(figsize=(14, 6))
        seller_performance.plot(kind="bar")
        plt.title("Top 10 Sellers by Revenue")
        plt.xlabel("Seller ID")
        plt.ylabel("Revenue")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/top_sellers.png")
        plt.close()

    if "delivery_delay_days" in temp.columns:
        plt.figure(figsize=(12, 6))
        sns.histplot(
            temp["delivery_delay_days"].dropna(),
            bins=50
        )
        plt.title("Delivery Delay Distribution")
        plt.xlabel("Delay in Days")
        plt.ylabel("Orders")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/delivery_delay.png")
        plt.close()

    numeric_df = temp.select_dtypes(include="number")

    if numeric_df.shape[1] > 1:
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            numeric_df.corr(),
            annot=False
        )
        plt.title("Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(f"{chart_path}/correlation_heatmap.png")
        plt.close()

    logger.info("Charts generated successfully.")