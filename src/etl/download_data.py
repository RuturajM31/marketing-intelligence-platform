# Download Kaggle Dataset
# downloads Kaggle dataset
# finds CSV files
# copies into project folder

import kagglehub
import shutil
from pathlib import Path

def download_dataset():

    path = kagglehub.dataset_download(
        "olistbr/brazilian-ecommerce"
    )

    print("Downloaded at:", path)

    src_path = Path(path)
    dest_path = Path("data/raw")

    dest_path.mkdir(parents=True, exist_ok=True)

    for file in src_path.glob("*.csv"):
        shutil.copy(file, dest_path)

    print("Files moved to data/raw")

if __name__ == "__main__":
    download_dataset()