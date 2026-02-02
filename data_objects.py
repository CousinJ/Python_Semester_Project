"""
Data Objects Module:
This module contains classes for storing data and loading data from CSV files.

"""


import pandas

class DataStorageObject:
    """
    An Object that stores data from a CSV file and converts it into a python 2d array of rows.
    """

    def __init__(self, data: pandas.DataFrame):
        """
        Initialize the Object with a pandas DataFrame.

        :param data: A pandas DataFrame containing the data

        attributes:
            *private* _df (pandas.DataFrame): The pandas DataFrame
            *private* _row_list (list): A list of rows from the DataFrame (2d array)

        """
        self._df = data
        self._row_list = data.values.tolist()
        
    @property
    def df(self) -> pandas.DataFrame:
        """
        Get the data frame from self.

        :return: The pandas DataFrame
        """
        return self._df
    
    @property
    def row_list(self) -> list:
        """
        Get the list of rows from self.

        :return: A list of rows from the DataFrame (2d array)
        """
        return self._df.values.tolist()
    
    




class DataLoader:
    """
    A class responsible for loading data from various sources.
    """

    def load_csv(self, file_path: str) -> pandas.DataFrame:
        """
        Load data from the specified CSV file.

        :param file_path: The path to the CSV file
        :return: Loaded data as a pandas DataFrame
        """
        return pandas.read_csv(file_path)  