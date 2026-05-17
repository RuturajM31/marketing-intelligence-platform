# ============================================
# EXTRACT LAYER (ETL - STEP 2)
# ============================================

# This file:
# - reads raw CSV files
# - converts them into pandas DataFrames
# - prepares data for transformation layer

import pandas as pd
from src.config import RAW_DATA_PATH
import logging

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# --------------------------------------------
# HELPER FUNCTION: Load single CSV file
# --------------------------------------------
def load_csv(file_name):
    """
    Reads CSV file from data/raw folder
    and returns pandas dataframe
    """

    try:
        file_path = RAW_DATA_PATH / file_name

        logger.info(f"Loading file: {file_name}")

        # Read CSV file
        df = pd.read_csv(file_path)

        logger.info(
            f"Loaded {file_name} successfully | Shape: {df.shape}"
        )

        return df

    except FileNotFoundError:
        logger.error(f"File not found: {file_name}")
        raise

    except Exception as e:
        logger.error(
            f"Error while reading {file_name}: {str(e)}"
        )
        raise


# --------------------------------------------
# MAIN FUNCTION: Extract all datasets
# --------------------------------------------
def extract_all_data():

    logger.info("Starting data extraction process...")

    # Dictionary storing all datasets
    data = {

        # Customer information
        "customers": load_csv(
            "olist_customers_dataset.csv"
        ),

        # Order transaction data
        "orders": load_csv(
            "olist_orders_dataset.csv"
        ),

        # Payment details
        "payments": load_csv(
            "olist_order_payments_dataset.csv"
        ),

        # Product order items
        "items": load_csv(
            "olist_order_items_dataset.csv"
        ),

        # Product metadata
        "products": load_csv(
            "olist_products_dataset.csv"
        ),
    }

    logger.info("All datasets extracted successfully")

    return data