"""
API CLIENT PLACEHOLDER

This project currently downloads data through KaggleHub in:
src/etl/download_data.py

In a larger project, reusable API clients could live here.
"""

import kagglehub


def download_kaggle_dataset(dataset_name: str) -> str:
    """
    Downloads a Kaggle dataset and returns the local path.
    """

    return kagglehub.dataset_download(dataset_name)