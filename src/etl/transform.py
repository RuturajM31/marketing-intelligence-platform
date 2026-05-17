def create_master_dataset(data):

    orders = data["orders"]
    payments = data["payments"]
    customers = data["customers"]
    items = data["items"]
    products = data["products"]

    print("Products columns:", products.columns)
    print("Items columns:", items.columns)

    # 1. Base fact table
    df = orders.merge(payments, on="order_id", how="left")

    # 2. Customer enrichment
    df = df.merge(customers, on="customer_id", how="left")

    # 3. Order items (THIS is where product_id comes from)
    df = df.merge(items, on="order_id", how="left")

    # 🔥 CRITICAL STEP: ensure product_id exists BEFORE merge
    print("Product ID exists in df before product merge:", "product_id" in df.columns)

    # 4. Product enrichment (THIS IS THE KEY FIX)
    df = df.merge(products, on="product_id", how="left")

    # 5. VERIFY AFTER MERGE
    print("After product merge columns contain product_category_name:",
        "product_category_name" in df.columns)

    return df