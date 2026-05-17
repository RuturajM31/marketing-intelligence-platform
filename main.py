import logging

from src.etl.download_data import download_dataset
from src.etl.extract import extract_all_data
from src.etl.transform import create_master_dataset
from src.etl.load import load_to_db
from src.services.data_quality import validate_data
from src.reporting.generate_reports import generate_report

# logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():

    logger.info("Starting Marketing Intelligence Pipeline")

    # STEP 1: Download dataset
    download_dataset()

    # STEP 2: Extract raw data
    data = extract_all_data()

    # STEP 3: Transform into single dataset
    df = create_master_dataset(data)

    # STEP 4: Validate data quality
    validate_data(df)

    # STEP 5: Load into database
    load_to_db(df, "master_data")

    # STEP 6: Run analytics + reporting
    kpis = generate_report(df)

    logger.info(f"Final KPIs: {kpis}")

if __name__ == "__main__":
    main()