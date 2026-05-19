import pandas as pd

from src.etl.transform import create_master_dataset


def test_create_master_dataset_prevents_data_explosion():
    """
    One order has:
    - 2 payment rows
    - 3 item rows

    Wrong raw merge would create:
    2 x 3 = 6 rows

    Correct transformation returns:
    1 row per order_id
    """

    orders = pd.DataFrame({
        "order_id": ["O1"],
        "customer_id": ["C1"],
        "order_status": ["delivered"],
        "order_purchase_timestamp": ["2023-01-01"],
        "order_approved_at": ["2023-01-01"],
        "order_delivered_carrier_date": ["2023-01-02"],
        "order_delivered_customer_date": ["2023-01-05"],
        "order_estimated_delivery_date": ["2023-01-06"]
    })

    customers = pd.DataFrame({
        "customer_id": ["C1"],
        "customer_unique_id": ["U1"],
        "customer_zip_code_prefix": [12345],
        "customer_city": ["Munich"],
        "customer_state": ["BY"]
    })

    payments = pd.DataFrame({
        "order_id": ["O1", "O1"],
        "payment_sequential": [1, 2],
        "payment_type": ["credit_card", "voucher"],
        "payment_installments": [1, 1],
        "payment_value": [100, 20]
    })

    items = pd.DataFrame({
        "order_id": ["O1", "O1", "O1"],
        "order_item_id": [1, 2, 3],
        "product_id": ["P1", "P2", "P3"],
        "seller_id": ["S1", "S1", "S2"],
        "shipping_limit_date": [
            "2023-01-02",
            "2023-01-02",
            "2023-01-02"
        ],
        "price": [50, 40, 30],
        "freight_value": [5, 4, 3]
    })

    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_category_name": [
            "electronics",
            "electronics",
            "books"
        ]
    })

    data = {
        "orders": orders,
        "customers": customers,
        "payments": payments,
        "items": items,
        "products": products
    }

    result = create_master_dataset(data)

    assert len(result) == 1
    assert result["order_id"].nunique() == 1
    assert result["payment_value"].iloc[0] == 120
    assert result["item_count"].iloc[0] == 3
    assert result["total_item_price"].iloc[0] == 120