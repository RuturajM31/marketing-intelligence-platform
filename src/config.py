from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data/raw"
PROCESSED_DATA_PATH = BASE_DIR / "data/processed"

DATABASE_URL = "sqlite:///marketing.db"

# where raw data is stored
# where processed data goes
# database location