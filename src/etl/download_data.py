# ============================================
# DOWNLOAD DATA LAYER (ETL - STEP 1)
# ============================================

# This module downloads dataset from Kaggle
# and stores it inside your local project folder

import kagglehub
import shutil
from pathlib import Path
import logging

# --------------------------------------------
# Logging setup (professional replacement for print)
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# --------------------------------------------
# MAIN FUNCTION: Download dataset
# --------------------------------------------
def download_dataset():
    """
    Downloads Kaggle dataset and moves CSV files
    into local data/raw directory
    """

    try:
        logger.info("Starting dataset download...")

        # Step 1: Download dataset from Kaggle
        path = kagglehub.dataset_download(
            "olistbr/brazilian-ecommerce"
        )

        logger.info(f"Dataset downloaded at: {path}")

        # Step 2: Convert to Path object (clean file handling)
        src_path = Path(path)

        # Step 3: Define destination folder in project
        dest_path = Path("data/raw")

        # Step 4: Create folder if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)

        # Step 5: Copy all CSV files into project folder
        csv_files = list(src_path.glob("*.csv"))

        if not csv_files:
            logger.warning("No CSV files found in dataset!")

        for file in csv_files:
            shutil.copy(file, dest_path)
            logger.info(f"Copied file: {file.name}")

        logger.info("All files successfully moved to data/raw")

    except Exception as e:
        # If anything fails, show clean error message
        logger.error(f"Error while downloading dataset: {str(e)}")
        raise


# --------------------------------------------
# Allows file to run independently
# --------------------------------------------
if __name__ == "__main__":
    download_dataset()