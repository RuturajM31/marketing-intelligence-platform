import logging

from sqlalchemy import create_engine

from src.config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)


def load_to_db(df, table_name: str) -> None:
    """
    Loads dataframe into SQLite.

    Current loading strategy:
        full refresh

    That means each run replaces the previous table.
    """

    logger.info(f"Loading data into database table: {table_name}")

    df.to_sql(
        table_name,
        con=engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        f"Loaded {len(df)} rows into table: {table_name}"
    )
    
    # This saves your final master dataset into SQLite.