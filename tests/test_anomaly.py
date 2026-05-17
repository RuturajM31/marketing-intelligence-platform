import pandas as pd

from src.analytics.anomaly import detect_anomalies


# ---------------------------------------------------
# Test anomaly detection
# ---------------------------------------------------
def test_detect_anomalies():

    df = pd.DataFrame({
        "payment_value": [100, 120, 130, 5000]
    })

    result = detect_anomalies(df)

    # Ensure anomaly column created
    assert "anomaly" in result.columns