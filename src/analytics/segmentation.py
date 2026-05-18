# ============================================
# CUSTOMER SEGMENTATION
# ============================================

"""
PURPOSE
-------
Groups customers based on behavior.

Used for:
- targeted marketing
- customer intelligence
- loyalty analysis
- retention strategy

Machine Learning Algorithm:
KMeans Clustering
"""

# ============================================
# IMPORTS
# ============================================

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


# ============================================
# CUSTOMER SEGMENTATION FUNCTION
# ============================================

def customer_segmentation(df):
    """
    Customer segmentation using KMeans clustering.

    FEATURES:
    ---------
    1. Total spending
    2. Purchase frequency

    INPUT:
    ------
    dataframe with:
    - customer_id
    - payment_value
    - order_id

    OUTPUT:
    -------
    customer-level dataframe
    with segment labels
    """

    logger.info(
        "Starting customer segmentation..."
    )

    # ============================================
    # CUSTOMER AGGREGATION
    # ============================================

    """
    We convert transaction-level data
    into customer-level behavior.

    Example:

    Customer A:
    spent = 1000
    orders = 5
    """

    customer = df.groupby(
        "customer_id"
    ).agg({

        # Total spend
        "payment_value": "sum",

        # Unique orders
        "order_id": "nunique"

    })

    # ============================================
    # FEATURE SCALING
    # ============================================

    """
    Scaling ensures:
    spending and orders
    have equal importance.
    """

    scaler = StandardScaler()

    scaled = scaler.fit_transform(customer)

    # ============================================
    # SAFE CLUSTER LOGIC
    # ============================================

    """
    Prevents this error:

    n_samples < n_clusters

    Example:
    3 customers cannot create 4 clusters.
    """

    k = min(4, len(customer))

    # Extra safety
    if k < 1:
        k = 1

    # ============================================
    # KMEANS MODEL
    # ============================================

    """
    n_clusters:
    number of customer groups

    random_state:
    ensures reproducible results

    n_init:
    improves clustering stability
    """

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    # Create segment labels
    customer["segment"] = model.fit_predict(
        scaled
    )

    logger.info(
        "Customer segmentation completed"
    )

    return customer