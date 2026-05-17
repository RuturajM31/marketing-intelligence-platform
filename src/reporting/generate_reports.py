from src.analytics.kpi import calculate_kpis
from src.reporting.export_charts import create_charts


def generate_report(df):

    print("Generating KPIs...")
    kpis = calculate_kpis(df)

    print("Generating charts...")
    create_charts(df)

    print("Report complete")

    return kpis