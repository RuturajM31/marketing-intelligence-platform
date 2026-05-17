from src.etl.download_data import download_dataset
from src.etl.extract import extract_all_data
from src.etl.transform import create_master_dataset
from src.etl.load import load_to_db
from src.reporting.generate_reports import generate_report
from src.utils.logger import logger


def main():

    logger.info("Starting Marketing Intelligence Pipeline")

    logger.info("Downloading dataset...")
    download_dataset()

    logger.info("Extracting data...")
    data = extract_all_data()

    logger.info("Transforming data...")
    df = create_master_dataset(data)

    logger.info("Loading data into database...")
    load_to_db(df, "master_data")

    logger.info("Running analytics & reporting...")
    kpis = generate_report(df)

    logger.info(f"Pipeline completed successfully. KPIs: {kpis}")


if __name__ == "__main__":
    main()