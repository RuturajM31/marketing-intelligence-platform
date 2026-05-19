import pandas as pd

from src.analytics.segmentation import customer_segmentation


def test_customer_segmentation():
    df = pd.DataFrame({
        "customer_unique_id": [
            "U1", "U1",
            "U2",
            "U3",
            "U4"
        ],
        "payment_value": [
            100, 200,
            300,
            400,
            500
        ],
        "order_id": [
            "O1", "O2",
            "O3",
            "O4",
            "O5"
        ],
        "order_purchase_timestamp": [
            "2023-01-01",
            "2023-02-01",
            "2023-01-15",
            "2023-03-01",
            "2023-04-01"
        ]
    })

    result = customer_segmentation(df)

    assert "segment" in result.columns
    assert "customer_unique_id" in result.columns
    assert result["customer_unique_id"].nunique() == 4
    assert result["segment"].nunique() > 0