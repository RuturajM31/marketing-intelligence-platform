import pandas as pd

from src.analytics.kpi import (
    average_order_value,
    repeat_customer_rate,
    total_orders,
    total_revenue,
    unique_customers
)


def test_total_revenue():
    df = pd.DataFrame({
        "payment_value": [100, 200, 300]
    })

    assert total_revenue(df) == 600


def test_total_orders():
    df = pd.DataFrame({
        "order_id": ["O1", "O2", "O2", "O3"]
    })

    assert total_orders(df) == 3


def test_average_order_value():
    df = pd.DataFrame({
        "order_id": ["O1", "O2", "O3"],
        "payment_value": [100, 200, 300]
    })

    assert average_order_value(df) == 200


def test_unique_customers_uses_customer_unique_id():
    df = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3"],
        "customer_unique_id": ["U1", "U1", "U2"]
    })

    assert unique_customers(df) == 2


def test_repeat_customer_rate_uses_customer_unique_id():
    df = pd.DataFrame({
        "order_id": ["O1", "O2", "O3"],
        "customer_unique_id": ["U1", "U1", "U2"]
    })

    assert repeat_customer_rate(df) == 50