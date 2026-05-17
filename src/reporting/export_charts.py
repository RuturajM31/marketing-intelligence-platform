import pandas as pd
import matplotlib.pyplot as plt
import os


def create_charts(df):

    os.makedirs("data/processed/charts", exist_ok=True)

    trend = df.groupby(
        pd.to_datetime(df["order_purchase_timestamp"]).dt.date
    )["payment_value"].sum()

    plt.figure()
    trend.plot()
    plt.title("Sales Trend")
    plt.savefig("data/processed/charts/sales.png")
    plt.close()