import pandas as pd

from src.analytics.anomaly import detect_anomalies


def test_detect_anomalies():
    df = pd.DataFrame({
        "payment_value": [
            100, 120, 130, 140, 150, 5000
        ]
    })

    result = detect_anomalies(df)

    assert "anomaly" in result.columns
    assert len(result) == len(df)