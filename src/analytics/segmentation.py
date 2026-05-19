import logging

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def customer_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Customer segmentation using RFM-style features.

    Uses:
        customer_unique_id
        recency
        frequency
        monetary value
    """

    required_columns = [
        "customer_unique_id",
        "order_id",
        "payment_value",
        "order_purchase_timestamp"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns for segmentation: {missing_columns}"
        )

    temp = df.copy()

    temp["order_purchase_timestamp"] = pd.to_datetime(
        temp["order_purchase_timestamp"],
        errors="coerce"
    )

    temp = temp.dropna(
        subset=["customer_unique_id", "order_purchase_timestamp"]
    )

    if temp.empty:
        return pd.DataFrame(
            columns=[
                "customer_unique_id",
                "recency",
                "frequency",
                "monetary",
                "segment"
            ]
        )

    reference_date = (
        temp["order_purchase_timestamp"].max()
        + pd.Timedelta(days=1)
    )

    customer = temp.groupby("customer_unique_id").agg(
        recency=(
            "order_purchase_timestamp",
            lambda x: (reference_date - x.max()).days
        ),
        frequency=("order_id", "nunique"),
        monetary=("payment_value", "sum")
    ).reset_index()

    if len(customer) == 1:
        customer["segment"] = 0
        return customer

    features = customer[
        ["recency", "frequency", "monetary"]
    ]

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    number_of_clusters = min(4, len(customer))

    model = KMeans(
        n_clusters=number_of_clusters,
        random_state=42,
        n_init=10
    )

    customer["segment"] = model.fit_predict(
        scaled_features
    )

    logger.info("Customer segmentation completed.")

    return customer