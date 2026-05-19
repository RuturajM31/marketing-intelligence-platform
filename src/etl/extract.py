import logging

import pandas as pd

from src.config import RAW_DATA_PATH

logger = logging.getLogger(__name__)


REQUIRED_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
}

OPTIONAL_FILES = {
    "sellers": "olist_sellers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def load_csv(file_name: str) -> pd.DataFrame:
    """
    Loads one CSV file from data/raw.
    """

    file_path = RAW_DATA_PATH / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    logger.info(f"Loading file: {file_name}")

    df = pd.read_csv(file_path)

    logger.info(f"Loaded {file_name} with shape {df.shape}")

    return df


def extract_all_data() -> dict[str, pd.DataFrame]:
    """
    Loads all required and optional Olist CSV files.
    """

    logger.info("Starting data extraction...")

    data = {}

    for key, file_name in REQUIRED_FILES.items():
        data[key] = load_csv(file_name)

    for key, file_name in OPTIONAL_FILES.items():
        file_path = RAW_DATA_PATH / file_name

        if file_path.exists():
            data[key] = pd.read_csv(file_path)
            logger.info(
                f"Loaded optional file {file_name} with shape {data[key].shape}"
            )
        else:
            logger.warning(f"Optional file not found: {file_name}")

    logger.info("Data extraction completed.")

    return data

# This loads raw CSV files into pandas DataFrames.