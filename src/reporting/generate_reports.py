import pandas as pd
import logging
from src.analytics.kpi import calculate_kpis
from src.reporting.export_charts import create_charts

logger = logging.getLogger(__name__)

def generate_report(df):
    """
    Generates business report:
    - KPIs
    - Charts
    - Saved output file
    """

    logger.info("Calculating KPIs...")
    kpis = calculate_kpis(df)

    # SAVE KPIs TO FILE (real business output)
    
    pd.DataFrame([kpis]).to_csv(
        "data/processed/kpis.csv",
        index=False
    )

    logger.info("Generating charts...")
    create_charts(df)

    logger.info("Report generation completed")

    return kpis