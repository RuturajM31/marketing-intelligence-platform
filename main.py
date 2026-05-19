import logging

from src.config import RAW_DATA_PATH
from src.etl.download_data import download_dataset
from src.etl.extract import extract_all_data
from src.etl.load import load_to_db
from src.etl.transform import create_master_dataset
from src.reporting.generate_reports import generate_report
from src.services.data_quality import validate_data

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def raw_data_available() -> bool:
    """
    Checks whether raw CSV files already exist.
    """

    return any(RAW_DATA_PATH.glob("*.csv"))


def main() -> None:
    """
    Main project pipeline.

    Flow:
        download data if missing
        extract CSVs
        transform into order-level master dataset
        validate data
        load to database
        generate reports
    """

    logger.info("Starting Marketing Intelligence Pipeline")

    if not raw_data_available():
        logger.info("Raw data missing. Downloading dataset...")
        download_dataset()
    else:
        logger.info("Raw data already available. Skipping download.")

    logger.info("Extracting data...")
    data = extract_all_data()

    logger.info("Transforming data...")
    master_df = create_master_dataset(data)

    logger.info("Validating data...")
    validation_report = validate_data(master_df)

    logger.info(
        f"Validation passed. Rows: {validation_report['row_count']}, "
        f"Columns: {validation_report['column_count']}"
    )

    logger.info("Loading data to database...")
    load_to_db(master_df, "master_data")

    logger.info("Generating reports...")
    kpis = generate_report(master_df)

    logger.info(f"Final KPIs: {kpis}")

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()