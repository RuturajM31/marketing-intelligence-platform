from sqlalchemy import create_engine

from src.config import DATABASE_URL


def get_engine():
    """
    Creates and returns a reusable SQLAlchemy engine.
    """

    return create_engine(DATABASE_URL)

# This centralizes database connection logic.