import logging

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def detect_payment_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects unusual payment values.
    """

    if "payment_value" not in df.columns:
        raise ValueError("payment_value column is required.")

    anomaly_df = df.copy()

    anomaly_df = anomaly_df.dropna(
        subset=["payment_value"]
    )

    if len(anomaly_df) < 5:
        anomaly_df["payment_anomaly"] = 1
        return anomaly_df

    scaler = StandardScaler()

    scaled_values = scaler.fit_transform(
        anomaly_df[["payment_value"]]
    )

    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    anomaly_df["payment_anomaly"] = model.fit_predict(
        scaled_values
    )

    return anomaly_df


def detect_delivery_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects extreme delivery delay values.
    """

    if "delivery_delay_days" not in df.columns:
        raise ValueError("delivery_delay_days column is required.")

    delivery_df = df.copy()

    threshold = delivery_df["delivery_delay_days"].quantile(0.99)

    delivery_df["delivery_anomaly"] = (
        delivery_df["delivery_delay_days"] > threshold
    )

    return delivery_df


def detect_seller_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects unusual seller-level performance.
    """

    if "main_seller_id" in df.columns:
        seller_column = "main_seller_id"
    elif "seller_id" in df.columns:
        seller_column = "seller_id"
    else:
        raise ValueError(
            "Seller anomaly detection requires main_seller_id or seller_id."
        )

    seller_df = df.dropna(
        subset=[seller_column]
    ).groupby(seller_column).agg(
        seller_revenue=("payment_value", "sum"),
        seller_orders=("order_id", "nunique")
    ).reset_index()

    if len(seller_df) < 5:
        seller_df["seller_anomaly"] = 1
        return seller_df

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        seller_df[["seller_revenue", "seller_orders"]]
    )

    model = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    seller_df["seller_anomaly"] = model.fit_predict(
        scaled_features
    )

    return seller_df


def run_all_anomaly_detection(df: pd.DataFrame) -> dict:
    """
    Runs all available anomaly detection modules.
    """

    results = {
        "payment_anomalies": detect_payment_anomalies(df)
    }

    if "delivery_delay_days" in df.columns:
        results["delivery_anomalies"] = detect_delivery_anomalies(df)

    if "main_seller_id" in df.columns or "seller_id" in df.columns:
        results["seller_anomalies"] = detect_seller_anomalies(df)

    return results


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple wrapper used by tests.
    Returns a dataframe with a column named anomaly.
    """

    result = detect_payment_anomalies(df)

    result = result.rename(
        columns={"payment_anomaly": "anomaly"}
    )

    return result