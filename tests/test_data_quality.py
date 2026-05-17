# TEST DATA QUALITY

import pandas as pd


# ---------------------------------------------------
# Test missing values detection
# ---------------------------------------------------
def test_missing_values():

    df = pd.DataFrame({
        "payment_value": [100, None, 300]
    })

    # Count missing values
    missing = df.isnull().sum().sum()

    # One missing value expected
    assert missing == 1 