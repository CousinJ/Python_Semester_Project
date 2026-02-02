"""
Data Objects Module:
This module contains classes for storing data and loading data from CSV files.

"""


import pandas
from pathlib import Path
  
class DataStorageObject:
    """
    An Object that stores data from a CSV file in a pandas DataFrame and provides a generator for iterating through rows as dictionaries.
    """

    def __init__(self, data: pandas.DataFrame):
        """
        Initialize the Object with a pandas DataFrame.

        :param data: A pandas DataFrame containing the data

        attributes:
            *private* _df (pandas.DataFrame): The pandas DataFrame
            

        """
        if data is None:
            raise ValueError("DataFrame cannot be None")
        if not isinstance(data, pandas.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        
        self._df = data
        
        
    @property
    def df(self) -> pandas.DataFrame:
        """
        Get the data frame from self.

        :return: The pandas DataFrame
        """
        return self._df
    
    
    
    def iter_rows_dict(self):
        """
        A Generator that yields each row as a dictionary.

        :yield: Each row as a dictionary
        """
        for _, row in self._df.iterrows():
            yield row.to_dict()




    def __iter__(self):
        """
        Make the DataStorageObject iterable.

        :return: iterator/generator of row dictionaries
        """
        return self.iter_rows_dict()
    


class DataLoader:
    """
    A class responsible for loading data from various sources.
    """

    def validate_csv_path(self, file_path: str) -> Path:
        """
        Validate the CSV file path before attempting to load it.
        Raises clear exceptions for common file issues.

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

    def load_csv(self, file_path: str) -> pandas.DataFrame:
        """
        Load data from the specified CSV file with robust error handling.

        :param file_path: The path to the CSV file
        :return: Loaded data as a pandas DataFrame
        :raises ValueError: if the CSV is empty/unreadable, malformed, or has encoding issues
        """
        path = self.validate_csv_path(file_path)

        try:
            return pandas.read_csv(path)
        except pandas.errors.EmptyDataError as e:
            raise ValueError(f"CSV has no readable data: {path}") from e
        except pandas.errors.ParserError as e:
            raise ValueError(f"CSV parsing failed (bad formatting): {path}") from e
        except UnicodeDecodeError as e:
            raise ValueError(f"CSV encoding error (try UTF-8): {path}") from e 