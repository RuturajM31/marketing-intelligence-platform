from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed"

DATABASE_PATH = BASE_DIR / "marketing.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# This file stores global paths. Other files import these variables instead of hardcoding paths.
# where raw data is stored
# where processed data goes
# database location