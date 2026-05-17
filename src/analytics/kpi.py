# KPIs:

## revenue
## order count
## average order value
## monthly sales trend

import pandas as pd

# Total Revenue

def total_revenue(df):
    return df["payment_value"].sum()

# Orders 

def total_orders(df):
    return df["order_id"].nunique()

# Average Order Value

def average_order_value(df):
    orders = df["order_id"].nunique()
    return df["payment_value"].sum() / orders if orders else 0

# Monthly Sales

def monthly_sales(df):

    df = df.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )

    df["month"] = df["order_purchase_timestamp"].dt.to_period("M")

    return df.groupby("month")["payment_value"].sum()

def calculate_kpis(df):

    return {
        "total_revenue": total_revenue(df),
        "total_orders": total_orders(df),
        "average_order_value": average_order_value(df)
    }
    
    
    
# calculate_kpis()
# ├── calls total_revenue()
# ├── calls total_orders()
# ├── calls average_order_value()