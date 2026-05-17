# Extract Layer - Read CSV
# reads raw CSV files
# converts them into DataFrames
# prepares them for transformation

import pandas as pd
from src.config import RAW_DATA_PATH
import logging

# --------------------------------------------
# Logging setup (professional replacement for print)
# --------------------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def load_csv(file_name):
    return pd.read_csv(RAW_DATA_PATH / file_name)


def extract_all_data():

    data = {
        "customers": load_csv("olist_customers_dataset.csv"),
        "orders": load_csv("olist_orders_dataset.csv"),
        "payments": load_csv("olist_order_payments_dataset.csv"),
        "items": load_csv("olist_order_items_dataset.csv"),
        "products": load_csv("olist_products_dataset.csv"),
    }

    return data