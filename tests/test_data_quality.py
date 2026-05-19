import pandas as pd
import pytest

from src.services.data_quality import (
    check_duplicates,
    check_missing_values,
    check_required_columns,
    validate_data
)


def test_check_missing_values():
    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "payment_value": [100, None, 300]
    })

    result = check_missing_values(df)

    assert result["order_id"] == 0
    assert result["payment_value"] == 1


def test_check_duplicates():
    df = pd.DataFrame({
        "order_id": [1, 1, 2],
        "payment_value": [100, 100, 200]
    })

    result = check_duplicates(df)

    assert result == 1


def test_check_required_columns_success():
    df = pd.DataFrame({
        "order_id": [1],
        "customer_unique_id": ["U1"],
        "payment_value": [100],
        "order_purchase_timestamp": ["2023-01-01"]
    })

    required_columns = [
        "order_id",
        "customer_unique_id",
        "payment_value",
        "order_purchase_timestamp"
    ]

    result = check_required_columns(df, required_columns)

    assert result == []


def test_check_required_columns_failure():
    df = pd.DataFrame({
        "order_id": [1],
        "payment_value": [100]
    })

    required_columns = [
        "order_id",
        "customer_unique_id",
        "payment_value"
    ]

    result = check_required_columns(df, required_columns)

    assert result == ["customer_unique_id"]


def test_validate_data_success():
    df = pd.DataFrame({
        "order_id": ["O1", "O2"],
        "customer_unique_id": ["U1", "U2"],
        "payment_value": [100, 200],
        "order_purchase_timestamp": [
            "2023-01-01",
            "2023-01-02"
        ]
    })

    result = validate_data(df)

    assert result["row_count"] == 2
    assert result["column_count"] == 4
    assert result["missing_columns"] == []
    assert result["is_valid"] is True


def test_validate_data_failure_missing_column():
    df = pd.DataFrame({
        "order_id": ["O1"],
        "payment_value": [100]
    })

    with pytest.raises(ValueError):
        validate_data(df)


def test_validate_data_failure_empty_dataframe():
    df = pd.DataFrame()

    with pytest.raises(ValueError):
        validate_data(df)