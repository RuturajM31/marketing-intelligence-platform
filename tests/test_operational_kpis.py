# ============================================================
# TEST OPERATIONAL KPIS
# Marketing Intelligence Platform
# ============================================================

"""
This test file checks the new operational KPI functions.

Operational KPIs are business health metrics such as:

- Delivered Orders
- Canceled Orders
- Unavailable Orders
- Cancellation Rate
- Delivery Success Rate
- Canceled Gross Payment Value

Why this test matters:
----------------------
The dashboard depends on these KPI functions.

If one calculation breaks, the dashboard can show wrong numbers.

This test uses a very small fake dataset so the expected answers
are easy to understand manually.
"""

# pandas is used here to create a small test dataframe.
# We do not need the real Olist dataset for unit tests.
import pandas as pd

# Import only the KPI functions we want to test.
from src.analytics.kpi import (
    delivered_orders,
    canceled_orders,
    unavailable_orders,
    cancellation_rate,
    delivery_success_rate,
    canceled_gross_payment_value,
)


def test_operational_kpis():
    """
    Tests delivered, canceled, unavailable, and operational rate calculations.

    Test data explanation:
    ----------------------
    We create 4 fake orders:

    O1 = delivered, payment 100
    O2 = canceled, payment 50
    O3 = delivered, payment 200
    O4 = unavailable, payment 80

    So manually we expect:

    Delivered Orders:
        O1 and O3 = 2

    Canceled Orders:
        O2 = 1

    Unavailable Orders:
        O4 = 1

    Total Orders:
        O1, O2, O3, O4 = 4

    Cancellation Rate:
        canceled orders / total orders * 100
        1 / 4 * 100 = 25%

    Delivery Success Rate:
        delivered orders / total orders * 100
        2 / 4 * 100 = 50%

    Canceled Gross Payment Value:
        payment_value where order_status is canceled
        O2 payment_value = 50
    """

    # Create a small fake dataframe.
    # This is enough to test the KPI logic.
    df = pd.DataFrame({
        "order_id": [
            "O1",
            "O2",
            "O3",
            "O4",
        ],
        "order_status": [
            "delivered",
            "canceled",
            "delivered",
            "unavailable",
        ],
        "payment_value": [
            100,
            50,
            200,
            80,
        ],
    })

    # Check delivered order count.
    # O1 and O3 are delivered, so expected result is 2.
    assert delivered_orders(df) == 2

    # Check canceled order count.
    # Only O2 is canceled, so expected result is 1.
    assert canceled_orders(df) == 1

    # Check unavailable order count.
    # Only O4 is unavailable, so expected result is 1.
    assert unavailable_orders(df) == 1

    # Check cancellation rate.
    # Formula: 1 canceled order / 4 total orders * 100 = 25.
    assert cancellation_rate(df) == 25

    # Check delivery success rate.
    # Formula: 2 delivered orders / 4 total orders * 100 = 50.
    assert delivery_success_rate(df) == 50

    # Check canceled gross payment value.
    # Only canceled order is O2, and its payment_value is 50.
    assert canceled_gross_payment_value(df) == 50