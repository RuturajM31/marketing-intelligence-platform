
# Groups customers into clusters:
## high value customers
## medium customers
## low value customers

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def customer_segmentation(df):

    customer = df.groupby("customer_id").agg({
        "payment_value": "sum",
        "order_id": "nunique"
    })

    scaler = StandardScaler()
    scaled = scaler.fit_transform(customer)

    model = KMeans(n_clusters=4, random_state=42, n_init=10)

    customer["segment"] = model.fit_predict(scaled)

    return customer