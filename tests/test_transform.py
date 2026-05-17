## Test Transformation

import pandas as pd

from src.etl.transform import create_master_dataset


# ---------------------------------------------------
# Test ETL merge logic
# ---------------------------------------------------
def test_create_master_dataset():

    # Mock orders table
    orders = pd.DataFrame({
        "order_id": [1],
        "customer_id": ["C1"]
    })

    # Mock payments table
    payments = pd.DataFrame({
        "order_id": [1],
        "payment_value": [500]
    })

    # Mock customers table
    customers = pd.DataFrame({
        "customer_id": ["C1"],
        "customer_city": ["Munich"]
    })

    # Mock items table
    items = pd.DataFrame({
        "order_id": [1],
        "product_id": ["P1"]
    })

    # Mock products table
    products = pd.DataFrame({
        "product_id": ["P1"],
        "product_category_name": ["electronics"]
    })

    # Create fake ETL dictionary
    data = {
        "orders": orders,
        "payments": payments,
        "customers": customers,
        "items": items,
        "products": products
    }

    # Run transformation
    df = create_master_dataset(data)

    # Validate merged columns exist
    assert "payment_value" in df.columns
    assert "customer_city" in df.columns
    assert "product_category_name" in df.columns

    # Validate row count
    assert len(df) == 1