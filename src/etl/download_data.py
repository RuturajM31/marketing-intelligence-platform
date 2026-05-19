import logging
import shutil
from pathlib import Path

import kagglehub

from src.config import RAW_DATA_PATH

logger = logging.getLogger(__name__)


def download_dataset(force: bool = False) -> None:
    """
    Downloads the Olist dataset from KaggleHub and copies CSV files
    into data/raw.

    If files already exist and force=False, download is skipped.
    """

    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    existing_csvs = list(RAW_DATA_PATH.glob("*.csv"))

    if existing_csvs and not force:
        logger.info("Raw CSV files already exist. Skipping download.")
        return

    logger.info("Downloading Olist dataset from KaggleHub...")

    kaggle_path = kagglehub.dataset_download(
        "olistbr/brazilian-ecommerce"
    )

    source_path = Path(kaggle_path)
    csv_files = list(source_path.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in downloaded path: {source_path}"
        )

    for file in csv_files:
        destination = RAW_DATA_PATH / file.name
        shutil.copy(file, destination)
        logger.info(f"Copied {file.name} to {destination}")

    logger.info("Dataset download completed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_dataset(force=True)
    
    # This downloads the dataset only if needed. force=True downloads again.