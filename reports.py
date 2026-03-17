"""
Report Module:
This module contains classes for objects responsible for displaying certain reports
from a DataStorageObject, report configurations, and a Report Generator that
will display the reports based on the configuration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from pyspark.sql.functions import avg, col, desc
from data_objects import DataStorageObject


@dataclass
class ReportConfig:
    """
    A configuration data class for report settings.

    Attributes:
        preview_lines (int): Number of lines to preview from the data frame.
        summary_stats (bool): Include summary statistics in the report.
        average_rainfall (bool): Include average rainfall calculation in the report.
        mean_rainfall_by_area (bool): Include a rainfall-by-area plot.
        top_temp_range_by_area (bool): Include a top temperature range plot.
    """
    preview_lines: int = 5
    summary_stats: bool = True
    average_rainfall: bool = True
    mean_rainfall_by_area: bool = False
    top_temp_range_by_area: bool = False


class ReportGenerator:
    """
    Class responsible for generating reports from a DataStorageObject.

    :param data_object: An instance of DataStorageObject
    :param config: An instance of ReportConfig
    """

    def __init__(self, data_object: DataStorageObject, config: ReportConfig):
        if not isinstance(config, ReportConfig):
            raise TypeError("config must be an instance of ReportConfig")

        if not isinstance(data_object, DataStorageObject):
            raise TypeError("data_object must be an instance of DataStorageObject")

        self.data_utility = data_object
        self.config = config
        self.report_actions: list[ReportAction] = []

    def build_actions(self) -> None:
        """
        Build the list of report actions based on the configuration by
        instantiating the concrete report objects.
        """
        self.report_actions.clear()

        if self.config.preview_lines > 0:
            self.report_actions.append(PreviewLines(self.config.preview_lines))
        if self.config.summary_stats:
            self.report_actions.append(SummaryStats())
        if self.config.average_rainfall:
            self.report_actions.append(AverageRainfall())
        if self.config.mean_rainfall_by_area:
            self.report_actions.append(MeanRainfallByArea())
        if self.config.top_temp_range_by_area:
            self.report_actions.append(TopTempRangeByLocation())

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
    def __init__(self) -> None:
        self.is_plot = False

    @abstractmethod
    def run(self, data: DataStorageObject) -> None:
        """
        Run the report action.

        :param data: The instance of the DataStorageObject
        """
        pass


class PreviewLines(ReportAction):
    """
    Concrete ReportAction class to preview lines from the DataStorageObject.
    """
    def __init__(self, num_lines: int):
        super().__init__()
        self.num_lines = num_lines

    def run(self, data: DataStorageObject) -> None:
        print(f"\n--- Previewing first {self.num_lines} rows ---")
        data.df.show(self.num_lines, truncate=False)


class SummaryStats(ReportAction):
    """
    Concrete ReportAction class to show summary statistics from the DataStorageObject.
    """
    def __init__(self):
        super().__init__()

    def run(self, data: DataStorageObject) -> None:
        print("\n--- Summary Statistics ---")
        data.df.describe().show(truncate=False)


class AverageRainfall(ReportAction):
    """
    Concrete ReportAction class to calculate average rainfall using PySpark aggregation.
    """
    def __init__(self):
        super().__init__()

    def run(self, data: DataStorageObject) -> None:
        print("\n--- Average Rainfall ---")

        if "Rainfall" not in data.df.columns:
            print("Rainfall column not found.")
            return

        result = data.df.select(avg(col("Rainfall")).alias("AverageRainfall"))
        result.show(truncate=False)


class MeanRainfallByArea(ReportAction):
    """
    Concrete ReportAction class to show mean rainfall by area from the
    DataStorageObject using Matplotlib. Generates a file into report_outputs.
    """
    def __init__(self, top_n: int = 15, output_file: str = "report_outputs/Mean_Rainfall_By_Area.png"):
        super().__init__()
        self.top_n = top_n
        self.output_file = output_file
        self.is_plot = True

    def run(self, data: DataStorageObject) -> None:
        try:
            if "Location" not in data.df.columns or "Rainfall" not in data.df.columns:
                print("Required columns 'Location' and/or 'Rainfall' not found.")
                return

            result = (
                data.df
                .groupBy("Location")
                .agg(avg(col("Rainfall")).alias("MeanRainfall"))
                .orderBy(desc("MeanRainfall"))
                .limit(self.top_n)
            )

            plot_df = result.toPandas()

            if plot_df.empty:
                print("No data available to plot mean rainfall by area.")
                return

            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            plt.figure(figsize=(12, 6))
            plt.bar(plot_df["Location"], plot_df["MeanRainfall"])
            plt.xticks(rotation=45, ha="right")
            plt.xlabel("Location")
            plt.ylabel("Mean Rainfall")
            plt.title(f"Top {self.top_n} Locations by Mean Rainfall")
            plt.tight_layout()
            plt.savefig(self.output_file)
            plt.close()

            print(f"Mean rainfall by area plot saved to {self.output_file}")

        except Exception as e:
            print(f"Error calculating mean rainfall by area: {e}")
            return


class TopTempRangeByLocation(ReportAction):
    """
    Concrete report action to show top temperature ranges by location from the
    DataStorageObject using Matplotlib. Generates a file into report_outputs.
    """
    def __init__(self, top_n: int = 15, output_file: str = "report_outputs/Top_Temp_Range_By_Location.png"):
        super().__init__()
        self.is_plot = True
        self.top_n = top_n
        self.output_file = output_file

    def run(self, data: DataStorageObject) -> None:
        try:
            required_columns = {"Location", "MaxTemp", "MinTemp"}
            if not required_columns.issubset(set(data.df.columns)):
                print("Required columns 'Location', 'MaxTemp', and/or 'MinTemp' not found.")
                return

            temp_range_df = data.df.withColumn("TempRange", col("MaxTemp") - col("MinTemp"))

            result = (
                temp_range_df
                .groupBy("Location")
                .agg(avg(col("TempRange")).alias("AvgTempRange"))
                .orderBy(desc("AvgTempRange"))
                .limit(self.top_n)
            )

            plot_df = result.toPandas()

            if plot_df.empty:
                print("No data available to plot top temperature range by location.")
                return

            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            plt.figure(figsize=(12, 6))
            plt.bar(plot_df["Location"], plot_df["AvgTempRange"])
            plt.xticks(rotation=45, ha="right")
            plt.xlabel("Location")
            plt.ylabel("Average Temperature Range")
            plt.title(f"Top {self.top_n} Locations by Average Temperature Range")
            plt.tight_layout()
            plt.savefig(self.output_file)
            plt.close()

            print(f"Top temperature range by location plot saved to {self.output_file}")

        except Exception as e:
            print(f"Error calculating temp range: {e}")