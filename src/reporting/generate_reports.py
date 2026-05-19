import logging
import os

import pandas as pd

from src.analytics.anomaly import run_all_anomaly_detection
from src.analytics.kpi import (
    calculate_kpis,
    monthly_order_growth,
    monthly_revenue_growth,
    monthly_sales
)
from src.analytics.segmentation import customer_segmentation
from src.reporting.export_charts import create_charts

logger = logging.getLogger(__name__)


def generate_report(df: pd.DataFrame) -> dict:
    """
    Generates all reporting outputs:
    - KPIs
    - monthly sales
    - revenue growth
    - order growth
    - customer segmentation
    - anomaly detection
    - charts
    """

    output_path = "data/processed"

    os.makedirs(output_path, exist_ok=True)

    logger.info("Generating KPIs...")

    kpis = calculate_kpis(df)

    pd.DataFrame([kpis]).to_csv(
        f"{output_path}/kpis.csv",
        index=False
    )

    logger.info("Generating monthly sales...")

    monthly_sales(df).reset_index().to_csv(
        f"{output_path}/monthly_sales.csv",
        index=False
    )

    monthly_revenue_growth(df).to_csv(
        f"{output_path}/monthly_revenue_growth.csv",
        index=False
    )

    monthly_order_growth(df).to_csv(
        f"{output_path}/monthly_order_growth.csv",
        index=False
    )

    logger.info("Generating customer segmentation...")

    segments = customer_segmentation(df)

    segments.to_csv(
        f"{output_path}/customer_segments.csv",
        index=False
    )

    logger.info("Running anomaly detection...")

    anomaly_results = run_all_anomaly_detection(df)

    for name, result_df in anomaly_results.items():
        result_df.to_csv(
            f"{output_path}/{name}.csv",
            index=False
        )

    logger.info("Generating charts...")

    create_charts(df)

    logger.info("Report generation completed.")

    return kpis