# ============================================
# REPORTING & VISUALIZATION LAYER
# ============================================

# This file:
# - creates business charts
# - exports analytics visuals
# - supports BI storytelling

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --------------------------------------------
# Professional chart styling
# --------------------------------------------
sns.set_style("whitegrid")


# ============================================
# MAIN CHART GENERATION FUNCTION
# ============================================

def create_charts(df):

    logger.info("Starting chart generation...")

    # ----------------------------------------
    # Create output directory
    # ----------------------------------------
    chart_path = "data/processed/charts"

    os.makedirs(chart_path, exist_ok=True)

    # ----------------------------------------
    # Convert date columns
    # ----------------------------------------
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )

    # ========================================
    # 1. DAILY REVENUE TREND (LINE CHART)
    # ========================================

    revenue_trend = df.groupby(
        df["order_purchase_timestamp"].dt.date
    )["payment_value"].sum()

    plt.figure(figsize=(14, 6))

    revenue_trend.plot()

    plt.title(
        "Daily Revenue Trend",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Date")
    plt.ylabel("Revenue")

    plt.tight_layout()

    plt.savefig(f"{chart_path}/daily_revenue_trend.png")

    plt.close()

    logger.info("Daily revenue trend chart created")

    # ========================================
    # 2. MONTHLY REVENUE (BAR CHART)
    # ========================================

    monthly = df.groupby(
        df["order_purchase_timestamp"].dt.to_period("M")
    )["payment_value"].sum()

    plt.figure(figsize=(14, 6))

    monthly.plot(kind="bar")

    plt.title(
        "Monthly Revenue Trend",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Month")
    plt.ylabel("Revenue")

    plt.tight_layout()

    plt.savefig(f"{chart_path}/monthly_revenue.png")

    plt.close()

    logger.info("Monthly revenue chart created")

    # ========================================
    # 3. TOP PRODUCT CATEGORIES (HORIZONTAL BAR)
    # ========================================

    if "product_category_name" in df.columns:

        top_categories = (
            df.groupby("product_category_name")[
                "payment_value"
            ]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        plt.figure(figsize=(12, 7))

        top_categories.plot(kind="barh")

        plt.title(
            "Top 10 Product Categories by Revenue",
            fontsize=16,
            fontweight="bold"
        )

        plt.xlabel("Revenue")

        plt.tight_layout()

        plt.savefig(f"{chart_path}/top_categories.png")

        plt.close()

        logger.info("Top categories chart created")

    # ========================================
    # 4. CUSTOMER ORDER DISTRIBUTION (HISTOGRAM)
    # ========================================

    customer_orders = df.groupby(
        "customer_id"
    )["order_id"].nunique()

    plt.figure(figsize=(12, 6))

    sns.histplot(
        customer_orders,
        bins=30,
        kde=True
    )

    plt.title(
        "Customer Order Frequency Distribution",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Orders Per Customer")
    plt.ylabel("Number of Customers")

    plt.tight_layout()

    plt.savefig(f"{chart_path}/customer_frequency.png")

    plt.close()

    logger.info("Customer frequency chart created")

    # ========================================
    # 5. PAYMENT METHOD DISTRIBUTION (PIE CHART)
    # ========================================

    payment_counts = df["payment_type"].value_counts()

    plt.figure(figsize=(8, 8))

    plt.pie(
        payment_counts,
        labels=payment_counts.index,
        autopct="%1.1f%%"
    )

    plt.title(
        "Payment Method Distribution",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()

    plt.savefig(f"{chart_path}/payment_methods.png")

    plt.close()

    logger.info("Payment methods chart created")

    # ========================================
    # 6. ORDER STATUS DISTRIBUTION (COUNTPLOT)
    # ========================================

    plt.figure(figsize=(12, 6))

    sns.countplot(
        data=df,
        x="order_status"
    )

    plt.title(
        "Order Status Distribution",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Order Status")
    plt.ylabel("Count")

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig(f"{chart_path}/order_status.png")

    plt.close()

    logger.info("Order status chart created")

    # ========================================
    # 7. SELLER PERFORMANCE (BAR CHART)
    # ========================================

    seller_perf = (
        df.groupby("seller_id")[
            "payment_value"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(14, 6))

    seller_perf.plot(kind="bar")

    plt.title(
        "Top 10 Sellers by Revenue",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Seller ID")
    plt.ylabel("Revenue")

    plt.tight_layout()

    plt.savefig(f"{chart_path}/top_sellers.png")

    plt.close()

    logger.info("Top seller chart created")

    # ========================================
    # 8. DELIVERY DELAY DISTRIBUTION
    # ========================================

    if (
        "order_delivered_customer_date" in df.columns
        and "order_estimated_delivery_date" in df.columns
    ):

        delivery_df = df.copy()

        delivery_df[
            "order_delivered_customer_date"
        ] = pd.to_datetime(
            delivery_df["order_delivered_customer_date"],
            errors="coerce"
        )

        delivery_df[
            "order_estimated_delivery_date"
        ] = pd.to_datetime(
            delivery_df["order_estimated_delivery_date"],
            errors="coerce"
        )

        delivery_df["delivery_delay_days"] = (
            delivery_df["order_delivered_customer_date"]
            - delivery_df["order_estimated_delivery_date"]
        ).dt.days

        plt.figure(figsize=(12, 6))

        sns.histplot(
            delivery_df["delivery_delay_days"].dropna(),
            bins=50
        )

        plt.title(
            "Delivery Delay Distribution",
            fontsize=16,
            fontweight="bold"
        )

        plt.xlabel("Delay (Days)")
        plt.ylabel("Orders")

        plt.tight_layout()

        plt.savefig(f"{chart_path}/delivery_delay.png")

        plt.close()

        logger.info("Delivery delay chart created")

    # ========================================
    # 9. CORRELATION HEATMAP
    # ========================================

    numeric_df = df.select_dtypes(include="number")

    plt.figure(figsize=(12, 8))

    sns.heatmap(
        numeric_df.corr(),
        annot=True,
        fmt=".2f"
    )

    plt.title(
        "Correlation Heatmap",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()

    plt.savefig(f"{chart_path}/correlation_heatmap.png")

    plt.close()

    logger.info("Correlation heatmap created")

    # ========================================
    # COMPLETED
    # ========================================

    logger.info(
        "All charts generated successfully"
    )