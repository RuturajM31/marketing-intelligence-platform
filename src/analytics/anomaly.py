# ============================================
# ANOMALY DETECTION LAYER
# ============================================

import pandas as pd
import logging

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================
# PAYMENT ANOMALY DETECTION
# ============================================

def detect_payment_anomalies(df):
    logger.info("Starting payment anomaly detection...")

    anomaly_df = df.copy()
    anomaly_df = anomaly_df.dropna(subset=["payment_value"])

    scaler = StandardScaler()
    scaled = scaler.fit_transform(anomaly_df[["payment_value"]])

    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    anomaly_df["payment_anomaly"] = model.fit_predict(scaled)

    anomaly_count = (anomaly_df["payment_anomaly"] == -1).sum()

    logger.info(f"Payment anomalies detected: {anomaly_count}")

    return anomaly_df


# ============================================
# DELIVERY ANOMALY DETECTION
# ============================================

def detect_delivery_anomalies(df):
    logger.info("Starting delivery anomaly detection...")

    delivery_df = df.copy()

    delivery_df["order_delivered_customer_date"] = pd.to_datetime(
        delivery_df["order_delivered_customer_date"],
        errors="coerce"
    )

    delivery_df["order_estimated_delivery_date"] = pd.to_datetime(
        delivery_df["order_estimated_delivery_date"],
        errors="coerce"
    )

    delivery_df["delivery_delay_days"] = (
        delivery_df["order_delivered_customer_date"]
        - delivery_df["order_estimated_delivery_date"]
    ).dt.days

    threshold = delivery_df["delivery_delay_days"].quantile(0.99)

    delivery_df["delivery_anomaly"] = (
        delivery_df["delivery_delay_days"] > threshold
    )

    anomaly_count = delivery_df["delivery_anomaly"].sum()

    logger.info(f"Delivery anomalies detected: {anomaly_count}")

    return delivery_df


# ============================================
# SELLER ANOMALY DETECTION
# ============================================

def detect_seller_anomalies(df):
    logger.info("Starting seller anomaly detection...")

    seller_df = df.groupby("seller_id").agg({
        "payment_value": "sum",
        "order_id": "nunique"
    }).reset_index()

    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        seller_df[["payment_value", "order_id"]]
    )

    model = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    seller_df["seller_anomaly"] = model.fit_predict(scaled)

    anomaly_count = (seller_df["seller_anomaly"] == -1).sum()

    logger.info(f"Seller anomalies detected: {anomaly_count}")

    return seller_df


# ============================================
# MASTER PIPELINE
# ============================================

def run_all_anomaly_detection(df):
    logger.info("Running complete anomaly detection...")

    results = {
        "payment_anomalies": detect_payment_anomalies(df),
        "delivery_anomalies": detect_delivery_anomalies(df),
        "seller_anomalies": detect_seller_anomalies(df)
    }

    logger.info("All anomaly detection completed")

    return results


# ============================================
# FIX FOR TEST COMPATIBILITY
# ============================================

def detect_anomalies(df):
    """
    Wrapper function for pytest compatibility.
    Runs full anomaly detection pipeline.
    """
    return run_all_anomaly_detection(df)