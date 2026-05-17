# test revenue/order calculations

import pandas as pd

from src.analytics.kpi import (
    total_revenue,
    total_orders,
    average_order_value
)


# ---------------------------------------------------
# Test total revenue calculation
# ---------------------------------------------------
def test_total_revenue():
    df = pd.DataFrame({
        "payment_value": [100, 200, 300]
    })

    # INTENTIONAL SAFE CHECK
    assert total_revenue(df) == 600


# ---------------------------------------------------
# Test total unique orders
# ---------------------------------------------------
def test_total_orders():

    df = pd.DataFrame({
        "order_id": [1, 2, 2, 3]
    })

    # Unique orders = 3
    assert total_orders(df) == 3


# ---------------------------------------------------
# Test average order value
# ---------------------------------------------------
def test_average_order_value():

    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "payment_value": [100, 200, 300]
    })

    # AOV = 600 / 3 = 200
    assert average_order_value(df) == 200