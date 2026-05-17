# ============================================
# LOAD LAYER (ETL - STEP 4)
# ============================================

# This file:
# - takes cleaned dataframe
# - stores it into SQLite database
# - simulates real data warehouse loading

from sqlalchemy import create_engine
from src.config import DATABASE_URL
import logging

# --------------------------------------------
# Logging setup
# --------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --------------------------------------------
# Create database engine connection
# --------------------------------------------
engine = create_engine(DATABASE_URL)


# --------------------------------------------
# MAIN FUNCTION: Load dataframe into database
# --------------------------------------------
def load_to_db(df, table_name):

    """
    Saves dataframe into SQLite database table
    """

    try:

        logger.info(
            f"Starting database load for table: {table_name}"
        )

        # ------------------------------------
        # Save dataframe into database
        # ------------------------------------
        df.to_sql(
            table_name,
            con=engine,
            if_exists="replace",
            index=False
        )

        logger.info(
            f"Successfully loaded data into table: {table_name}"
        )

        logger.info(
            f"Rows loaded: {len(df)}"
        )

    except Exception as e:

        logger.error(
            f"Database loading failed: {str(e)}"
        )

        raise