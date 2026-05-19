# ============================================
# TRANSFORM LAYER (ETL - STEP 3)
# ============================================

# This file:
# - merges multiple datasets
# - cleans data
# - converts dates
# - creates final analytics-ready dataset

import pandas as pd
import logging

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# --------------------------------------------
# MAIN TRANSFORMATION FUNCTION
# --------------------------------------------
def create_master_dataset(data):

    logger.info("Starting data transformation process...")

    # ----------------------------------------
    # STEP 1: Load individual datasets
    # ----------------------------------------
    
    orders = data["orders"]
    payments = data["payments"]
    customers = data["customers"]
    items = data["items"]
    products = data["products"]

    # ----------------------------------------
    # STEP 2: Check columns before merge
    # ----------------------------------------
    
    logger.info(f"Products columns: {products.columns}")
    logger.info(f"Items columns: {items.columns}")

    # ----------------------------------------
    # STEP 3: Merge orders + payments
    # Creates financial transaction layer
    # ----------------------------------------
    
    df = orders.merge(
        payments,
        on="order_id",
        how="left"
    )

    # ----------------------------------------
    # STEP 4: Merge customer information
    # Adds customer demographics/location
    # ----------------------------------------
    
    df = df.merge(
        customers,
        on="customer_id",
        how="left"
    )

    # ----------------------------------------
    # STEP 5: Merge order items
    # Adds product_id and seller_id
    # ----------------------------------------
    
    df = df.merge(
        items,
        on="order_id",
        how="left"
    )

    # ----------------------------------------
    # STEP 6: Verify product_id exists
    # ----------------------------------------
    
    logger.info(
        f"Product ID exists before product merge: "
        f"{'product_id' in df.columns}"
    )

    # ----------------------------------------
    # STEP 7: Merge product information
    # Adds product category and attributes
    # ----------------------------------------
    
    df = df.merge(
        products,
        on="product_id",
        how="left"
    )

    # ----------------------------------------
    # STEP 8: Verify successful product merge
    # ----------------------------------------
    
    logger.info(
        f"After product merge, product_category_name exists: "
        f"{'product_category_name' in df.columns}"
    )

    # ----------------------------------------
    # STEP 9: Convert date columns
    # VERY IMPORTANT for analytics
    # ----------------------------------------
    
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in date_columns:

        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    logger.info("Date conversion completed")

    # ----------------------------------------
    # STEP 10: Remove duplicate rows
    # ----------------------------------------
    
    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    logger.info(
        f"Removed {before - after} duplicate rows"
    )

    # ----------------------------------------
    # STEP 11: Final safety check
    # ----------------------------------------
    
    assert not df.empty, "Final dataframe is empty!"

    logger.info(
        f"Transformation completed successfully. "
        f"Final shape: {df.shape}"
    )

    return df