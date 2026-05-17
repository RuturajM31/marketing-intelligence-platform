# ============================================
# ANOMALY DETECTION LAYER
# ============================================

# This file:
# - detects unusual transactions
# - identifies suspicious orders
# - finds operational anomalies
# - supports fraud analysis

import pandas as pd
import logging

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ============================================
# PAYMENT ANOMALY DETECTION
# ============================================

def detect_payment_anomalies(df):

    """
    Detect unusual payment values
    using Isolation Forest
    """

    logger.info(
        "Starting payment anomaly detection..."
    )

    anomaly_df = df.copy()

    # ----------------------------------------
    # Remove missing payment values
    # ----------------------------------------
    anomaly_df = anomaly_df.dropna(
        subset=["payment_value"]
    )

    # ----------------------------------------
    # Scale numerical data
    # ML models work better with scaled data
    # ----------------------------------------
    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        anomaly_df[["payment_value"]]
    )

    # ----------------------------------------
    # Isolation Forest Model
    # -1 = anomaly
    # 1 = normal
    # ----------------------------------------
    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    anomaly_df["payment_anomaly"] = (
        model.fit_predict(scaled)
    )

    # ----------------------------------------
    # Count anomalies
    # ----------------------------------------
    anomaly_count = (
        anomaly_df["payment_anomaly"] == -1
    ).sum()

    logger.info(
        f"Payment anomalies detected: {anomaly_count}"
    )

    return anomaly_df


# ============================================
# DELIVERY DELAY ANOMALIES
# ============================================

def detect_delivery_anomalies(df):

    """
    Detect extremely delayed deliveries
    """

    logger.info(
        "Starting delivery anomaly detection..."
    )

    delivery_df = df.copy()

    # ----------------------------------------
    # Convert date columns
    # ----------------------------------------
    delivery_df[
        "order_delivered_customer_date"
    ] = pd.to_datetime(
        delivery_df[
            "order_delivered_customer_date"
        ],
        errors="coerce"
    )

    delivery_df[
        "order_estimated_delivery_date"
    ] = pd.to_datetime(
        delivery_df[
            "order_estimated_delivery_date"
        ],
        errors="coerce"
    )

    # ----------------------------------------
    # Calculate delay in days
    # ----------------------------------------
    delivery_df["delivery_delay_days"] = (
        delivery_df[
            "order_delivered_customer_date"
        ]
        - delivery_df[
            "order_estimated_delivery_date"
        ]
    ).dt.days

    # ----------------------------------------
    # Detect top 1% delays
    # ----------------------------------------
    threshold = (
        delivery_df[
            "delivery_delay_days"
        ].quantile(0.99)
    )

    delivery_df["delivery_anomaly"] = (
        delivery_df[
            "delivery_delay_days"
        ] > threshold
    )

    anomaly_count = (
        delivery_df["delivery_anomaly"]
    ).sum()

    logger.info(
        f"Delivery anomalies detected: "
        f"{anomaly_count}"
    )

    return delivery_df


# ============================================
# SELLER PERFORMANCE ANOMALIES
# ============================================

def detect_seller_anomalies(df):

    """
    Detect sellers with unusually
    high or low revenue patterns
    """

    logger.info(
        "Starting seller anomaly detection..."
    )

    seller_df = df.groupby(
        "seller_id"
    ).agg({

        "payment_value": "sum",
        "order_id": "nunique"

    }).reset_index()

    # ----------------------------------------
    # Scale features
    # ----------------------------------------
    scaler = StandardScaler()

    scaled = scaler.fit_transform(

        seller_df[
            ["payment_value", "order_id"]
        ]

    )

    # ----------------------------------------
    # Isolation Forest
    # ----------------------------------------
    model = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    seller_df["seller_anomaly"] = (
        model.fit_predict(scaled)
    )

    anomaly_count = (
        seller_df["seller_anomaly"] == -1
    ).sum()

    logger.info(
        f"Seller anomalies detected: "
        f"{anomaly_count}"
    )

    return seller_df


# ============================================
# MASTER ANOMALY FUNCTION
# ============================================

def run_all_anomaly_detection(df):

    """
    Runs all anomaly detection pipelines
    """

    logger.info(
        "Running complete anomaly detection..."
    )

    results = {

        "payment_anomalies":
            detect_payment_anomalies(df),

        "delivery_anomalies":
            detect_delivery_anomalies(df),

        "seller_anomalies":
            detect_seller_anomalies(df)
    }

    logger.info(
        "All anomaly detection completed"
    )

    return results