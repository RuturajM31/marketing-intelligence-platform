# Anomaly Detection
## unusual payments
## outliers
## possible fraud

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def detect_anomalies(df):

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[["payment_value"]])

    model = IsolationForest(contamination=0.02, random_state=42)
    df["anomaly"] = model.fit_predict(scaled)

    return df