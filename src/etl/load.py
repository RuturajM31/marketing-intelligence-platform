# Takes Clean Data and stores in SQLite Database

from sqlalchemy import create_engine
from src.config import DATABASE_URL
import logging

# --------------------------------------------
# Logging setup (professional replacement for print)
# --------------------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

engine = create_engine(DATABASE_URL)

def load_to_db(df, table_name):

    df.to_sql(
        table_name,
        con=engine,
        if_exists="replace",
        index=False
    )