import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _mode_or_none(series: pd.Series):
    """
    Returns the most common value in a Series.
    If no value exists, returns None.
    """

    mode_values = series.dropna().mode()

    if mode_values.empty:
        return None

    return mode_values.iloc[0]


def create_master_dataset(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Creates an order-level master dataset.

    Final grain:
        One row = one order_id

    Why:
        payments can have multiple rows per order
        items can have multiple rows per order

    If raw payments and raw items are merged directly,
    pandas creates a many-to-many join and duplicates rows.

    Correct approach:
        aggregate payments to order level
        aggregate items to order level
        then merge
    """

    logger.info("Starting transformation process...")

    orders = data["orders"].copy()
    customers = data["customers"].copy()
    payments = data["payments"].copy()
    items = data["items"].copy()
    products = data["products"].copy()

    # Start with orders because our final table is one row per order.
    master = orders.copy()

    # Add customer information, including customer_unique_id.
    master = master.merge(
        customers,
        on="customer_id",
        how="left"
    )

    # Aggregate payments to one row per order.
    payments_agg = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        payment_installments=("payment_installments", "sum"),
        payment_count=("payment_sequential", "count"),
        primary_payment_type=("payment_type", _mode_or_none),
        payment_types=(
            "payment_type",
            lambda x: ", ".join(sorted(x.dropna().astype(str).unique()))
        )
    ).reset_index()

    master = master.merge(
        payments_agg,
        on="order_id",
        how="left"
    )

    # Add product category translations if available.
    products_enriched = products.copy()

    if "category_translation" in data:
        translation = data["category_translation"].copy()

        products_enriched = products_enriched.merge(
            translation,
            on="product_category_name",
            how="left"
        )

    # Add product metadata to item-level table before aggregation.
    items_enriched = items.merge(
        products_enriched,
        on="product_id",
        how="left"
    )

    # Add seller metadata if available.
    if "sellers" in data:
        sellers = data["sellers"].copy()

        items_enriched = items_enriched.merge(
            sellers,
            on="seller_id",
            how="left"
        )

    # Aggregate items to one row per order.
    items_agg = items_enriched.groupby("order_id").agg(
        item_count=("order_item_id", "count"),
        total_item_price=("price", "sum"),
        total_freight_value=("freight_value", "sum"),
        unique_products=("product_id", "nunique"),
        unique_sellers=("seller_id", "nunique"),
        main_product_id=("product_id", _mode_or_none),
        main_seller_id=("seller_id", _mode_or_none),
        main_product_category=("product_category_name", _mode_or_none),
    ).reset_index()

    if "product_category_name_english" in items_enriched.columns:
        category_english = items_enriched.groupby("order_id").agg(
            main_product_category_english=(
                "product_category_name_english",
                _mode_or_none
            )
        ).reset_index()

        items_agg = items_agg.merge(
            category_english,
            on="order_id",
            how="left"
        )

    if "seller_state" in items_enriched.columns:
        seller_location = items_enriched.groupby("order_id").agg(
            main_seller_state=("seller_state", _mode_or_none),
            main_seller_city=("seller_city", _mode_or_none)
        ).reset_index()

        items_agg = items_agg.merge(
            seller_location,
            on="order_id",
            how="left"
        )

    master = master.merge(
        items_agg,
        on="order_id",
        how="left"
    )

    # Aggregate reviews if available.
    if "reviews" in data:
        reviews = data["reviews"].copy()

        reviews_agg = reviews.groupby("order_id").agg(
            review_score=("review_score", "mean"),
            review_count=("review_id", "count"),
            has_review_comment=(
                "review_comment_message",
                lambda x: x.notna().any()
            )
        ).reset_index()

        master = master.merge(
            reviews_agg,
            on="order_id",
            how="left"
        )

    # Add customer geolocation if available.
    if "geolocation" in data:
        geolocation = data["geolocation"].copy()

        geo_agg = geolocation.groupby(
            "geolocation_zip_code_prefix"
        ).agg(
            customer_lat=("geolocation_lat", "mean"),
            customer_lng=("geolocation_lng", "mean")
        ).reset_index()

        master = master.merge(
            geo_agg,
            left_on="customer_zip_code_prefix",
            right_on="geolocation_zip_code_prefix",
            how="left"
        )

        master = master.drop(
            columns=["geolocation_zip_code_prefix"],
            errors="ignore"
        )

    # Convert date columns to datetime.
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:
        if column in master.columns:
            master[column] = pd.to_datetime(
                master[column],
                errors="coerce"
            )

    # Create delivery features.
    if (
        "order_delivered_customer_date" in master.columns
        and "order_estimated_delivery_date" in master.columns
    ):
        master["delivery_delay_days"] = (
            master["order_delivered_customer_date"]
            - master["order_estimated_delivery_date"]
        ).dt.days

        master["is_late_delivery"] = (
            master["delivery_delay_days"] > 0
        )

    if (
        "order_delivered_customer_date" in master.columns
        and "order_purchase_timestamp" in master.columns
    ):
        master["delivery_time_days"] = (
            master["order_delivered_customer_date"]
            - master["order_purchase_timestamp"]
        ).dt.days

    # Fill numeric nulls caused by missing joins.
    numeric_fill_zero = [
        "payment_value",
        "payment_installments",
        "payment_count",
        "item_count",
        "total_item_price",
        "total_freight_value",
        "unique_products",
        "unique_sellers",
        "review_count"
    ]

    for column in numeric_fill_zero:
        if column in master.columns:
            master[column] = master[column].fillna(0)

    # Safety check: master table must remain one row per order.
    duplicate_orders = master["order_id"].duplicated().sum()

    if duplicate_orders > 0:
        raise ValueError(
            f"Data explosion detected: {duplicate_orders} duplicate order_id rows found."
        )

    logger.info(
        f"Transformation completed successfully. Final shape: {master.shape}"
    )

    return master

# This is the most important file. It fixes the many-to-many join problem.