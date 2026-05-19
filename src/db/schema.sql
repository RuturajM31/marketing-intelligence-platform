-- SQLite schema reference.
-- pandas.to_sql creates the actual table automatically.
-- This file documents the intended master_data structure.

CREATE TABLE IF NOT EXISTS master_data (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    customer_unique_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TEXT,
    payment_value REAL,
    item_count INTEGER,
    total_item_price REAL,
    total_freight_value REAL,
    main_product_category TEXT,
    main_product_category_english TEXT,
    main_seller_id TEXT,
    review_score REAL,
    delivery_delay_days REAL
);