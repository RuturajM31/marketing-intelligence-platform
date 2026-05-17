# DATA QUALITY LAYER
# This file checks if data is clean before analytics runs

import logging

logger = logging.getLogger(__name__)

def check_missing_values(df):
    """
    Checks how many missing values exist in each column
    """
    missing = df.isnull().sum()
    logger.info(f"Missing values per column:\n{missing}")
    return missing


def check_duplicates(df):
    """
    Checks duplicate rows in dataset
    """
    dup = df.duplicated().sum()
    logger.info(f"Duplicate rows found: {dup}")
    return dup


def validate_data(df):
    """
    Runs ALL data quality checks together
    """
    logger.info("Starting data validation...")

    check_missing_values(df)
    check_duplicates(df)

    logger.info("Data validation completed successfully")