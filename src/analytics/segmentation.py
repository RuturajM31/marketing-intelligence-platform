from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def customer_segmentation(df):
    """
    Groups customers into segments based on behavior:
    - Spending (payment_value)
    - Purchase frequency (order_id)
    """

    # STEP 1: Create customer-level dataset
    customer = df.groupby("customer_id").agg({
        "payment_value": "sum",   # total money spent
        "order_id": "nunique"     # number of orders
    })

    # STEP 2: Normalize data (important for ML)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(customer)

    # STEP 3: SAFE CLUSTER COUNT
    # ensures we never ask for more clusters than data points
    k = min(4, len(customer))

    # STEP 4: Apply KMeans clustering
    model = KMeans(n_clusters=k, random_state=42)
    customer["segment"] = model.fit_predict(scaled)

    return customer