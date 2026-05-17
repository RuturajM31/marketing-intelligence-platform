import pandas as pd

from src.analytics.segmentation import customer_segmentation


# ---------------------------------------------------
# Test customer segmentation
# ---------------------------------------------------
def test_customer_segmentation():

    # Create sample customer transaction dataset
    df = pd.DataFrame({
        "customer_id": [
            "C1", "C1",
            "C2",
            "C3",
            "C4"
        ],

        "payment_value": [
            100, 200,
            300,
            400,
            500
        ],

        "order_id": [
            1, 2,
            3,
            4,
            5
        ]
    })

    # Run segmentation
    segmented = customer_segmentation(df)

    # Validate segment column exists
    assert "segment" in segmented.columns

    # Ensure clusters were created
    assert segmented["segment"].nunique() > 0