"""
Report Module:
This module contains classes for objects responsible for displaying certain reports from a DataStorageObject, Report configurations, and a Report Generator that
will display the reports based on the configuration.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from data_objects import DataStorageObject

@dataclass
class ReportConfig:

    """
    A configuration data class for report settings.

    Attributes:
        preview_lines (int): Number of lines to preview from the data frame.
        summary_stats (bool):  Include summary statistics in the report.
        show_row_count (bool):  Show the total row count in the report.
    """
    preview_lines: int = 5
    summary_stats: bool = True
    show_row_count: bool = True




class ReportGenerator:
    """
    Class responsible for generating reports from a DataStorageObject.

    param duo: An instance of DataStorageObject
    param config: An instance of ReportConfig

    attributes:
        data_utility (DataStorageObject): The data storage object   
        config (ReportConfig): The report configuration
        report_actions (list[ReportAction]): List of report actions to execute
    """

    def __init__(self, duo: DataStorageObject, config: ReportConfig):
        """
        Initialize the ReportGenerator with a DataStorageObject and ReportConfig.

        :param duo: An instance of DataStorageObject
        :param config: An instance of ReportConfig
        """
        self.data_utility = duo
        self.config = config
        self.report_actions: list[ReportAction] = []

    def build_actions(self) -> None:
        """
        Build the list of report actions based on the configuration by instantiating the concrete report objects (PreviewLines, SummaryStats, ShowRowCount).
        """
        self.report_actions.clear()

        if self.config.preview_lines > 0:
            self.report_actions.append(PreviewLines(self.config.preview_lines))
        if self.config.summary_stats:
            self.report_actions.append(SummaryStats())
        if self.config.show_row_count:
            self.report_actions.append(ShowRowCount())

            
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

class ShowRowCount(ReportAction):

    """
    Concrete ReportAction class to show the total row count from the DataStorageObject.
    """
    def run(self, data) -> None:
        print(f"Total number of rows: {len(data.row_list)}")


