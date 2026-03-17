"""
Data Objects Module:
This module contains classes for storing data and loading data from CSV files.
"""

from pathlib import Path
from pyspark.sql import DataFrame, SparkSession


class DataStorageObject:
    """
    An object that stores data from a CSV file in a PySpark DataFrame.
    """

    def __init__(self, data: DataFrame):
        """
        Initialize the object with a PySpark DataFrame.

        :param data: A PySpark DataFrame containing the data

        attributes:
            _df (DataFrame): The PySpark DataFrame
        """
        if data is None:
            raise ValueError("DataFrame cannot be None")
        if not isinstance(data, DataFrame):
            raise TypeError(f"Expected pyspark DataFrame, got {type(data).__name__}")

        self._df = data

    @property
    def df(self) -> DataFrame:
        """
        Get the PySpark DataFrame.

        :return: The PySpark DataFrame
        """
        return self._df


class DataLoader:
    """
    A class responsible for loading data from CSV files into PySpark DataFrames.
    """

    def validate_csv_path(self, file_path: str) -> Path:
        """
        Validate the CSV file path before attempting to load it.

        :param file_path: path to the CSV file
        :return: Path object for the validated file
        :raises ValueError: if path is empty, file is empty, or file is not .csv
        :raises FileNotFoundError: if file does not exist
        :raises IsADirectoryError: if a directory path is provided
        """
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string")

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        if path.is_dir():
            raise IsADirectoryError(f"Expected a file but got a directory: {path}")

        if path.stat().st_size == 0:
            raise ValueError(f"CSV file is empty: {path}")

        if path.suffix.lower() != ".csv":
            raise ValueError(f"Expected a .csv file, got: {path.name}")

        return path

    def load_csv(self, file_path: str) -> DataFrame:
        """
        Load data from the specified CSV file into a PySpark DataFrame.

        :param file_path: The path to the CSV file
        :return: Loaded data as a PySpark DataFrame
        """
        path = self.validate_csv_path(file_path)

        try:
            spark = SparkSession.builder.appName("WeatherProjectPySpark").getOrCreate()
            return spark.read.csv(str(path), header=True, inferSchema=True)
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {path}") from e