"""
Report Module:
This module contains classes for objects responsible for displaying certain reports from a DataStorageObject, Report configurations, and a Report Generator that
will display the reports based on the configuration.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas
from data_objects import DataStorageObject

@dataclass
class ReportConfig:

    """
    A configuration data class for report settings.

    Attributes:
        preview_lines (int): Number of lines to preview from the data frame.
        summary_stats (bool):  Include summary statistics in the report.
        average_rainfall (bool): Include average rainfall calculation in the report.
    """
    preview_lines: int = 5
    summary_stats: bool = True
    average_rainfall: bool = True




class ReportGenerator:
    """
    Class responsible for generating reports from a DataStorageObject.

    param duo: An instance of DataStorageObject
    param config: An instance of ReportConfig

    attributes:
        data_utility (DataStorageObject): The data storage object   
        config (ReportConfig): The report configuration
        report_actions (list[ReportAction]): List of report actions to execute




    >>> import pandas as pd
    >>> from data_objects import DataStorageObject
    >>> from reports import ReportConfig, ReportGenerator

    >>> df = DataStorageObject(pd.DataFrame({'A': [1], 'B': [2]}))
    >>> config = ReportConfig(preview_lines=1, summary_stats=True, average_rainfall=False)
    >>> gen = ReportGenerator(df, config)
    >>> gen.build_actions()
    >>> len(gen.report_actions) > 0
    True
    """

    def __init__(self, data_object: DataStorageObject, config: ReportConfig):

        """
        Class responsible for generating reports from a DataStorageObject.

        :param data_object: DataStorageObject instance
        :param config: ReportConfig instance
        """

        if not isinstance(config, ReportConfig):
            raise TypeError("config must be an instance of ReportConfig")
        
        if not isinstance(data_object, DataStorageObject):
            raise TypeError("data_object must be an instance of DataStorageObject")
        
        self.data_utility = data_object
        self.config = config
        self.report_actions: list[ReportAction] = []

    def build_actions(self) -> None:
        """
        Build the list of report actions based on the configuration by instantiating the concrete report objects.
        """
        self.report_actions.clear()

        if self.config.preview_lines > 0:
            self.report_actions.append(PreviewLines(self.config.preview_lines))
        if self.config.summary_stats:
            self.report_actions.append(SummaryStats())
        if self.config.average_rainfall:
            self.report_actions.append(AverageRainfall())
        

            
    def run_report(self) -> None:
        """
        Run the report by executing all configured report actions.
        """
        self.build_actions()
        for action in self.report_actions:
            action.run(self.data_utility)









class ReportAction(ABC):

    """
    Abstract base class for report actions.
    """
    @abstractmethod
    def run(self, data) -> None:
        """
        Docstring for run
        
        :param data: The instance of the DatastorageObject
        
        """
        pass

class PreviewLines(ReportAction):
    """
    Concrete ReportAction class to preview lines from the DataStorageObject.
    """
    def __init__(self, num_lines: int):
        self.num_lines = num_lines

    def run(self, data) -> None:
        print(data.df.head(self.num_lines))


class SummaryStats(ReportAction):
    """
    Concrete ReportAction class to show summary statistics from the DataStorageObject.
    """
    def run(self, data) -> None:
        print(data.df.describe())

class AverageRainfall(ReportAction):
    """
    Concrete ReportAction class to show average rainfall from the DataStorageObject.
    """
    def run(self, data) -> None:
        total = 0
        count = 0
        for row in data:  
            val = row.get("Rainfall")

            if val is not None:
                if isinstance(val, (int, float)) and pandas.notna(val):
                    total += val
                    count += 1
            else:
                continue
        print("Avg Rainfall:", total / count if count else "N/A")



