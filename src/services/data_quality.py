import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def check_missing_values(df: pd.DataFrame) -> pd.Series:
    """
    Counts missing values in each column.
    """

    missing_values = df.isnull().sum()

    logger.info(f"Missing values per column:\n{missing_values}")

    return missing_values


def check_duplicates(df: pd.DataFrame) -> int:
    """
    Counts fully duplicated rows.
    """

    duplicate_count = int(df.duplicated().sum())

    logger.info(f"Duplicate rows found: {duplicate_count}")

    return duplicate_count


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str]
) -> list[str]:
    """
    Checks whether required columns exist.
    """

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        logger.warning(
            f"Missing required columns: {missing_columns}"
        )

    return missing_columns


def validate_data(
    df: pd.DataFrame,
    required_columns: Optional[list[str]] = None
) -> dict:
    """
    Runs all data quality checks.

    Raises an error if:
        dataframe is empty
        required columns are missing
    """

    logger.info("Starting data validation...")

    if required_columns is None:
        required_columns = [
            "order_id",
            "customer_unique_id",
            "payment_value",
            "order_purchase_timestamp"
        ]

    if df.empty:
        raise ValueError(
            "Data validation failed: dataframe is empty."
        )

    missing_values = check_missing_values(df)
    duplicate_count = check_duplicates(df)
    missing_columns = check_required_columns(
        df,
        required_columns
    )

    validation_report = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_values": missing_values,
        "duplicate_count": duplicate_count,
        "missing_columns": missing_columns,
        "is_valid": len(missing_columns) == 0
    }

    if missing_columns:
        raise ValueError(
            f"Data validation failed. Missing columns: {missing_columns}"
        )

    logger.info("Data validation completed successfully")

    return validation_report

# This makes data validation testable.