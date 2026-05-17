# ============================================
# CUSTOMER SEGMENTATION LAYER
# ============================================

# This file:
# - performs RFM analysis
# - clusters customers using ML
# - identifies VIP customers
# - supports targeted marketing

import pandas as pd
import logging

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ============================================
# BUILD RFM TABLE
# ============================================

def build_rfm_table(df):

    """
    Creates customer-level RFM metrics

    R = Recency
    F = Frequency
    M = Monetary
    """

    logger.info(
        "Building RFM customer table..."
    )

    rfm_df = df.copy()

    # ----------------------------------------
    # Convert order timestamp
    # ----------------------------------------
    rfm_df["order_purchase_timestamp"] = (
        pd.to_datetime(
            rfm_df["order_purchase_timestamp"],
            errors="coerce"
        )
    )

    # ----------------------------------------
    # Snapshot date
    # latest date in dataset
    # ----------------------------------------
    snapshot_date = (
        rfm_df["order_purchase_timestamp"]
        .max()
    )

    # ----------------------------------------
    # Build RFM metrics
    # ----------------------------------------
    rfm = rfm_df.groupby("customer_id").agg({

        # Recency
        "order_purchase_timestamp":
            lambda x: (
                snapshot_date - x.max()
            ).days,

        # Frequency
        "order_id":
            "nunique",

        # Monetary
        "payment_value":
            "sum"

    })

    # ----------------------------------------
    # Rename columns
    # ----------------------------------------
    rfm.columns = [

        "Recency",
        "Frequency",
        "Monetary"

    ]

    logger.info(
        f"RFM table created "
        f"for {len(rfm)} customers"
    )

    return rfm


# ============================================
# KMEANS CUSTOMER CLUSTERING
# ============================================

def customer_segmentation(df):

    """
    Segments customers using:

    - Recency
    - Frequency
    - Monetary

    Machine Learning:
    - StandardScaler
    - KMeans Clustering
    """

    logger.info(
        "Starting customer segmentation..."
    )

    # ----------------------------------------
    # Build RFM table
    # ----------------------------------------
    rfm = build_rfm_table(df)

    # ----------------------------------------
    # Scale numerical features
    # Important for clustering quality
    # ----------------------------------------
    scaler = StandardScaler()

    scaled = scaler.fit_transform(

        rfm[[
            "Recency",
            "Frequency",
            "Monetary"
        ]]

    )

    # ----------------------------------------
    # Safe cluster count
    # prevents ML crash
    # ----------------------------------------
    k = min(4, len(rfm))

    logger.info(
        f"Using {k} customer clusters"
    )

    # ----------------------------------------
    # Train KMeans model
    # ----------------------------------------
    model = KMeans(

        n_clusters=k,
        random_state=42,
        n_init=10

    )

    # ----------------------------------------
    # Predict customer segments
    # ----------------------------------------
    rfm["segment"] = (

        model.fit_predict(scaled)

    )

    logger.info(
        "Customer segmentation completed"
    )

    return rfm


# ============================================
# SEGMENT LABELING
# ============================================

def label_customer_segments(rfm):

    """
    Adds business-friendly labels
    to ML-generated clusters
    """

    logger.info(
        "Labelling customer segments..."
    )

    # ----------------------------------------
    # Average spending by segment
    # ----------------------------------------
    segment_summary = rfm.groupby(
        "segment"
    )["Monetary"].mean()

    # ----------------------------------------
    # Sort segments by spending
    # ----------------------------------------
    ranked_segments = (
        segment_summary
        .sort_values()
        .index
        .tolist()
    )

    # ----------------------------------------
    # Business labels
    # ----------------------------------------
    labels = {

        ranked_segments[0]:
            "Low Value",

        ranked_segments[1]:
            "Mid Value",

        ranked_segments[2]:
            "High Value",

        ranked_segments[3]:
            "VIP"

    }

    # ----------------------------------------
    # Apply labels
    # ----------------------------------------
    rfm["segment_label"] = (
        rfm["segment"].map(labels)
    )

    logger.info(
        "Customer labels assigned"
    )

    return rfm


# ============================================
# SEGMENT SUMMARY
# ============================================

def segment_summary(rfm):

    """
    Creates business summary
    for each customer segment
    """

    logger.info(
        "Generating segment summary..."
    )

    summary = rfm.groupby(
        "segment_label"
    ).agg({

        "Recency": "mean",
        "Frequency": "mean",
        "Monetary": "mean"

    }).round(2)

    logger.info(
        "Segment summary completed"
    )

    return summary


# ============================================
# MASTER PIPELINE
# ============================================

def run_customer_segmentation(df):

    """
    Complete segmentation pipeline
    """

    logger.info(
        "Running full segmentation pipeline..."
    )

    # ----------------------------------------
    # ML segmentation
    # ----------------------------------------
    rfm = customer_segmentation(df)

    # ----------------------------------------
    # Add business labels
    # ----------------------------------------
    rfm = label_customer_segments(rfm)

    # ----------------------------------------
    # Segment business summary
    # ----------------------------------------
    summary = segment_summary(rfm)

    logger.info(
        "Customer segmentation pipeline completed"
    )

    return {

        "rfm_table": rfm,

        "segment_summary": summary

    }