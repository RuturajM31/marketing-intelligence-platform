import logging
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

from src.config import PROCESSED_DATA_PATH

logger = logging.getLogger(__name__)


# ==========================================================
# GLOBAL CHART STYLE
# ==========================================================

def set_chart_style():
    """
    Applies a clean professional style to all charts.

    Why this matters:
    Default matplotlib charts often look academic or childish.
    A consistent style makes the output look closer to BI reporting.
    """

    sns.set_theme(
        style="whitegrid",
        context="talk"
    )

    plt.rcParams.update({
        "figure.figsize": (14, 7),
        "axes.titlesize": 18,
        "axes.labelsize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })


def currency_formatter(value, _):
    """
    Formats large numbers as currency-style values.

    Example:
    1200000 -> 1.2M
    45000   -> 45.0K
    """

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{value:.0f}"


def save_chart(file_name: str):
    """
    Saves chart into data/processed/charts.
    """

    chart_dir = PROCESSED_DATA_PATH / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    output_path = chart_dir / file_name

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    logger.info(f"Saved chart: {output_path}")


def wrap_labels(labels, width=24):
    """
    Wraps long category names so they are readable in charts.
    """

    return [
        textwrap.fill(str(label), width=width)
        for label in labels
    ]


# ==========================================================
# CHART 1: MONTHLY REVENUE TREND
# ==========================================================

def plot_monthly_revenue(df: pd.DataFrame):
    """
    Shows monthly revenue trend.

    Business question:
    Is revenue growing, shrinking, or unstable over time?
    """

    required = {
        "order_purchase_timestamp",
        "payment_value"
    }

    if not required.issubset(df.columns):
        logger.warning("Skipping monthly revenue chart: missing columns.")
        return

    temp = df.copy()

    temp["order_purchase_timestamp"] = pd.to_datetime(
        temp["order_purchase_timestamp"],
        errors="coerce"
    )

    temp = temp.dropna(subset=["order_purchase_timestamp"])

    monthly = (
        temp.groupby(
            temp["order_purchase_timestamp"].dt.to_period("M")
        )["payment_value"]
        .sum()
        .sort_index()
    )

    monthly.index = monthly.index.astype(str)

    fig, ax = plt.subplots()

    ax.plot(
        monthly.index,
        monthly.values,
        marker="o",
        linewidth=2.5
    )

    ax.fill_between(
        monthly.index,
        monthly.values,
        alpha=0.12
    )

    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

    ax.tick_params(axis="x", rotation=45)

    # Annotate last value
    if len(monthly) > 0:
        last_x = len(monthly.index) - 1
        last_y = monthly.values[-1]

        ax.annotate(
            f"{currency_formatter(last_y, None)}",
            xy=(last_x, last_y),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=11,
            weight="bold"
        )

    save_chart("01_monthly_revenue_trend.png")


# ==========================================================
# CHART 2: TOP PRODUCT CATEGORIES
# ==========================================================

def plot_top_categories(df: pd.DataFrame):
    """
    Shows top product categories by revenue.

    Business question:
    Which categories drive the most revenue?
    """

    category_column = None

    if "main_product_category_english" in df.columns:
        category_column = "main_product_category_english"
    elif "main_product_category" in df.columns:
        category_column = "main_product_category"

    if category_column is None or "payment_value" not in df.columns:
        logger.warning("Skipping category chart: missing category/payment columns.")
        return

    top_categories = (
        df.dropna(subset=[category_column])
        .groupby(category_column)["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(14, 8))

    bars = ax.barh(
        wrap_labels(top_categories.index),
        top_categories.values
    )

    ax.set_title("Top 10 Product Categories by Revenue")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(currency_formatter))

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {currency_formatter(width, None)}",
            va="center",
            fontsize=10,
            weight="bold"
        )

    save_chart("02_top_categories_by_revenue.png")


# ==========================================================
# CHART 3: ORDER STATUS DISTRIBUTION
# ==========================================================

def plot_order_status(df: pd.DataFrame):
    """
    Shows order status distribution.

    Business question:
    What percentage of orders are delivered, canceled, or unavailable?
    """

    if "order_status" not in df.columns:
        logger.warning("Skipping order status chart: missing order_status.")
        return

    status_counts = (
        df["order_status"]
        .value_counts(normalize=True)
        .mul(100)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(
        status_counts.index,
        status_counts.values
    )

    ax.set_title("Order Status Distribution")
    ax.set_xlabel("Share of Orders (%)")
    ax.set_ylabel("")

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {width:.1f}%",
            va="center",
            fontsize=10,
            weight="bold"
        )

    save_chart("03_order_status_distribution.png")


# ==========================================================
# CHART 4: PAYMENT METHOD DISTRIBUTION
# ==========================================================

def plot_payment_methods(df: pd.DataFrame):
    """
    Shows primary payment method distribution.

    Business question:
    Which payment methods are most commonly used?
    """

    payment_column = None

    if "primary_payment_type" in df.columns:
        payment_column = "primary_payment_type"
    elif "payment_type" in df.columns:
        payment_column = "payment_type"

    if payment_column is None:
        logger.warning("Skipping payment chart: missing payment type column.")
        return

    payment_share = (
        df[payment_column]
        .dropna()
        .value_counts(normalize=True)
        .mul(100)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(
        payment_share.index,
        payment_share.values
    )

    ax.set_title("Primary Payment Method Share")
    ax.set_xlabel("Share of Orders (%)")
    ax.set_ylabel("")

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {width:.1f}%",
            va="center",
            fontsize=10,
            weight="bold"
        )

    save_chart("04_payment_method_share.png")


# ==========================================================
# CHART 5: CUSTOMER FREQUENCY DISTRIBUTION
# ==========================================================

def plot_customer_frequency(df: pd.DataFrame):
    """
    Shows how many orders customers place.

    Business question:
    Are customers mostly one-time buyers or repeat buyers?
    """

    required = {
        "customer_unique_id",
        "order_id"
    }

    if not required.issubset(df.columns):
        logger.warning("Skipping customer frequency chart: missing columns.")
        return

    customer_orders = (
        df.groupby("customer_unique_id")["order_id"]
        .nunique()
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    sns.histplot(
        customer_orders,
        bins=30,
        kde=False,
        ax=ax
    )

    ax.set_title("Customer Purchase Frequency")
    ax.set_xlabel("Orders per Customer")
    ax.set_ylabel("Number of Customers")

    median_orders = customer_orders.median()

    ax.axvline(
        median_orders,
        linestyle="--",
        linewidth=2
    )

    ax.annotate(
        f"Median: {median_orders:.0f}",
        xy=(median_orders, ax.get_ylim()[1] * 0.85),
        xytext=(8, 0),
        textcoords="offset points",
        fontsize=11,
        weight="bold"
    )

    save_chart("05_customer_purchase_frequency.png")


# ==========================================================
# CHART 6: DELIVERY DELAY DISTRIBUTION
# ==========================================================

def plot_delivery_delay(df: pd.DataFrame):
    """
    Shows delivery delay distribution.

    Business question:
    How often are deliveries late, and how severe are delays?
    """

    if "delivery_delay_days" not in df.columns:
        logger.warning("Skipping delivery delay chart: missing delivery_delay_days.")
        return

    delivery_delay = df["delivery_delay_days"].dropna()

    if delivery_delay.empty:
        logger.warning("Skipping delivery delay chart: no valid delay values.")
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    sns.histplot(
        delivery_delay,
        bins=50,
        kde=True,
        ax=ax
    )

    ax.axvline(
        0,
        linestyle="--",
        linewidth=2
    )

    ax.set_title("Delivery Delay Distribution")
    ax.set_xlabel("Delay in Days")
    ax.set_ylabel("Number of Orders")

    ax.annotate(
        "Late deliveries →",
        xy=(0, ax.get_ylim()[1] * 0.85),
        xytext=(10, 0),
        textcoords="offset points",
        fontsize=11,
        weight="bold"
    )

    save_chart("06_delivery_delay_distribution.png")


# ==========================================================
# CHART 7: TOP SELLERS BY REVENUE
# ==========================================================

def plot_top_sellers(df: pd.DataFrame):
    """
    Shows top sellers by revenue.

    Business question:
    Is revenue concentrated among a few sellers?
    """

    seller_column = None

    if "main_seller_id" in df.columns:
        seller_column = "main_seller_id"
    elif "seller_id" in df.columns:
        seller_column = "seller_id"

    if seller_column is None or "payment_value" not in df.columns:
        logger.warning("Skipping seller chart: missing seller/payment columns.")
        return

    seller_revenue = (
        df.dropna(subset=[seller_column])
        .groupby(seller_column)["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(14, 8))

    bars = ax.barh(
        seller_revenue.index.astype(str),
        seller_revenue.values
    )

    ax.set_title("Top 10 Sellers by Revenue")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(currency_formatter))

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {currency_formatter(width, None)}",
            va="center",
            fontsize=10,
            weight="bold"
        )

    save_chart("07_top_sellers_by_revenue.png")


# ==========================================================
# CHART 8: AVERAGE REVIEW SCORE BY CATEGORY
# ==========================================================

def plot_review_score_by_category(df: pd.DataFrame):
    """
    Shows average review score by top product categories.

    Business question:
    Which categories create better or worse customer experience?
    """

    category_column = None

    if "main_product_category_english" in df.columns:
        category_column = "main_product_category_english"
    elif "main_product_category" in df.columns:
        category_column = "main_product_category"

    required = {
        category_column,
        "review_score"
    }

    if category_column is None or not required.issubset(df.columns):
        logger.warning("Skipping review chart: missing category/review columns.")
        return

    review_data = (
        df.dropna(subset=[category_column, "review_score"])
        .groupby(category_column)
        .agg(
            average_review_score=("review_score", "mean"),
            orders=("order_id", "nunique")
        )
        .query("orders >= 50")
        .sort_values("average_review_score", ascending=False)
        .head(10)
        .sort_values("average_review_score")
    )

    if review_data.empty:
        logger.warning("Skipping review chart: insufficient review data.")
        return

    fig, ax = plt.subplots(figsize=(14, 8))

    bars = ax.barh(
        wrap_labels(review_data.index),
        review_data["average_review_score"]
    )

    ax.set_title("Highest Rated Product Categories")
    ax.set_xlabel("Average Review Score")
    ax.set_ylabel("")
    ax.set_xlim(0, 5)

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {width:.2f}",
            va="center",
            fontsize=10,
            weight="bold"
        )

    save_chart("08_review_score_by_category.png")


# ==========================================================
# MASTER FUNCTION
# ==========================================================

def create_charts(df: pd.DataFrame) -> None:
    """
    Creates all business charts.

    This function is called by:
        src/reporting/generate_reports.py
    """

    logger.info("Starting professional chart generation...")

    set_chart_style()

    plot_monthly_revenue(df)
    plot_top_categories(df)
    plot_order_status(df)
    plot_payment_methods(df)
    plot_customer_frequency(df)
    plot_delivery_delay(df)
    plot_top_sellers(df)
    plot_review_score_by_category(df)

    logger.info("All professional charts generated successfully.")