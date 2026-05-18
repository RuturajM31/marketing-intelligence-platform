# ============================================
# ANOMALY DETECTION LAYER
# ============================================

"""
PURPOSE OF THIS FILE
--------------------
This module detects unusual behavior in the ecommerce dataset.

We detect:
1. Payment anomalies
   -> unusually high/low transactions

2. Delivery anomalies
   -> extremely delayed deliveries

3. Seller anomalies
   -> suspicious seller behavior

4. Simple anomaly wrapper
   -> used by pytest unit tests & CI/CD
"""

# ============================================
# IMPORTS
# ============================================

import pandas as pd
import logging

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ============================================
# LOGGER CONFIGURATION
# ============================================

"""
Logging helps us track:
- pipeline progress
- errors
- anomaly counts
- debugging information

Professional projects always use logging
instead of print().
"""

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


# ============================================
# PAYMENT ANOMALY DETECTION
# ============================================

def detect_payment_anomalies(df):
    """
    Detect unusual payment transactions.

    INPUT:
    ------
    df -> pandas dataframe

    REQUIRED COLUMN:
    ----------------
    payment_value

    OUTPUT:
    -------
    dataframe with:
    payment_anomaly column

    HOW IT WORKS:
    -------------
    1. Scale payment values
    2. Train Isolation Forest
    3. Predict anomalies

    IsolationForest returns:
    1  -> normal
    -1 -> anomaly
    """

    logger.info("Starting payment anomaly detection...")

    # Create safe dataframe copy
    anomaly_df = df.copy()

    # Remove rows where payment_value is missing
    anomaly_df = anomaly_df.dropna(
        subset=["payment_value"]
    )

    # ============================================
    # FEATURE SCALING
    # ============================================

    """
    WHY SCALING?

    ML models work better when values
    are normalized.

    Example:
    100 vs 10000 can create imbalance.

    StandardScaler converts values into:
    mean = 0
    std = 1
    """

    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        anomaly_df[["payment_value"]]
    )

    # ============================================
    # ISOLATION FOREST MODEL
    # ============================================

    """
    contamination=0.02
    means:
    assume 2% data are anomalies
    """

    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    # Fit model + predict anomalies
    anomaly_df["payment_anomaly"] = model.fit_predict(
        scaled
    )

    # Count anomalies
    anomaly_count = (
        anomaly_df["payment_anomaly"] == -1
    ).sum()

    logger.info(
        f"Payment anomalies detected: {anomaly_count}"
    )

    return anomaly_df


# ============================================
# DELIVERY ANOMALY DETECTION
# ============================================

def detect_delivery_anomalies(df):
    """
    Detect abnormal delivery delays.

    REQUIRED COLUMNS:
    -----------------
    order_delivered_customer_date
    order_estimated_delivery_date

    OUTPUT:
    -------
    delivery_delay_days
    delivery_anomaly
    """

    logger.info("Starting delivery anomaly detection...")

    delivery_df = df.copy()

    # ============================================
    # CONVERT TO DATETIME
    # ============================================

    """
    We convert text dates into
    actual datetime format.

    errors='coerce'
    converts invalid dates into NaT
    instead of crashing.
    """

    delivery_df["order_delivered_customer_date"] = pd.to_datetime(
        delivery_df["order_delivered_customer_date"],
        errors="coerce"
    )

    delivery_df["order_estimated_delivery_date"] = pd.to_datetime(
        delivery_df["order_estimated_delivery_date"],
        errors="coerce"
    )

    # ============================================
    # DELIVERY DELAY CALCULATION
    # ============================================

    """
    Positive value:
    late delivery

    Negative value:
    early delivery
    """

    delivery_df["delivery_delay_days"] = (
        delivery_df["order_delivered_customer_date"]
        - delivery_df["order_estimated_delivery_date"]
    ).dt.days

    # ============================================
    # EXTREME OUTLIERS
    # ============================================

    """
    quantile(0.99)
    means:
    top 1% worst delays
    """

    threshold = delivery_df[
        "delivery_delay_days"
    ].quantile(0.99)

    delivery_df["delivery_anomaly"] = (
        delivery_df["delivery_delay_days"] > threshold
    )

    anomaly_count = (
        delivery_df["delivery_anomaly"]
    ).sum()

    logger.info(
        f"Delivery anomalies detected: {anomaly_count}"
    )

    return delivery_df


# ============================================
# SELLER ANOMALY DETECTION
# ============================================

def detect_seller_anomalies(df):
    """
    Detect suspicious seller behavior.

    FEATURES USED:
    --------------
    1. Total revenue
    2. Order count

    OUTPUT:
    -------
    seller_anomaly column
    """

    logger.info("Starting seller anomaly detection...")

    # ============================================
    # SELLER LEVEL AGGREGATION
    # ============================================

    """
    We aggregate seller performance first.

    Example:
    Seller A:
    - 500 orders
    - €100,000 revenue
    """

    seller_df = df.groupby(
        "seller_id"
    ).agg({
        "payment_value": "sum",
        "order_id": "nunique"
    }).reset_index()

    # Scale data
    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        seller_df[
            ["payment_value", "order_id"]
        ]
    )

    # Train model
    model = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    seller_df["seller_anomaly"] = model.fit_predict(
        scaled
    )

    anomaly_count = (
        seller_df["seller_anomaly"] == -1
    ).sum()

    logger.info(
        f"Seller anomalies detected: {anomaly_count}"
    )

    return seller_df


# ============================================
# MASTER PIPELINE
# ============================================

def run_all_anomaly_detection(df):
    """
    Runs all anomaly modules together.

    RETURNS:
    --------
    dictionary containing:
    - payment anomalies
    - delivery anomalies
    - seller anomalies
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


# ============================================
# SIMPLE TEST WRAPPER
# ============================================

def detect_anomalies(df):
    """
    SIMPLE VERSION FOR UNIT TESTS

    WHY THIS EXISTS:
    ----------------
    Your pytest test expects:
    - one dataframe
    - one column called 'anomaly'

    But production pipeline returns
    multiple anomaly datasets.

    So this wrapper keeps
    CI/CD compatibility.
    """

    logger.info(
        "Running simple anomaly detection for tests..."
    )

    anomaly_df = df.copy()

    anomaly_df = anomaly_df.dropna(
        subset=["payment_value"]
    )

    # Scale values
    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        anomaly_df[["payment_value"]]
    )

    # Train model
    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    # IMPORTANT:
    # Unit test expects this exact name
    anomaly_df["anomaly"] = model.fit_predict(
        scaled
    )

    logger.info(
        "Simple anomaly detection completed"
    )

    return anomaly_df