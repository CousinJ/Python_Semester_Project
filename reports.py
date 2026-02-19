"""
Report Module:
This module contains classes for objects responsible for displaying certain reports from a DataStorageObject, Report configurations, and a Report Generator that
will display the reports based on the configuration.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
import pandas
import matplotlib.pyplot as plt
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
    mean_rainfall_by_area: bool = False
    top_temp_range_by_area: bool = False
  




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




#plot mean rainfall for each area
class MeanRainfallByArea(ReportAction):
    """
    Concrete ReportAction class to show mean rainfall by area from the DataStorageObject using Matplotlib, generates file into "report_outputs" dir.
    """
    def __init__(self, top_n: int = 15, output_file: str = "report_outputs/Mean_Rainfall_By_Area.png"):
        self.top_n = top_n
        self.output_file = output_file

    def run(self, data) -> None:
        try:
            # group by location to find rainfall averages for each area
            df = data.df.copy()
            df = df.dropna(subset=["Location", "Rainfall"])
            mean_rainfall = df.groupby("Location")["Rainfall"].mean()
            #Sort and get top N locations
            mean_rainfall = mean_rainfall.sort_values(ascending=False).head(self.top_n)

                # Plotting
            plt.figure(figsize=(10, 5))
            mean_rainfall.plot(kind='bar')
            plt.title("Mean Rainfall by Area")
            plt.xlabel("Location")
            plt.ylabel("Mean Rainfall")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(self.output_file)
            print(f"Mean_rainfall_by_area chart successfully saved to {self.output_file}")

        except Exception as e:
            print(f"Error calculating mean rainfall by area: {e}")
            return
       
#plot top temp range by location
class TopTempRangeByLocation(ReportAction):
    """
    Concrete report action to show top temperature ranges by location from the DataStorageObject using Matplotlib, generates file into "report_outputs" dir.
    """

    def __init__(self, top_n: int = 15, output_file: str = "report_outputs/Top_Temp_Range_By_Location.png"):
        self.top_n = top_n
        self.output_file = output_file

    def run(self, data) -> None:
        try:
            rows = data.df.to_dict(orient="records")

            #clean data with filter
            valid_rows = list(filter(
                lambda r: (
                    r.get("Location") is not None
                    and pandas.notna(r.get("MinTemp"))
                    and pandas.notna(r.get("MaxTemp"))
                ),
                rows
            ))

            if not valid_rows:
                print("No valid temperature rows found.")
                return
            

            # transform rows into ranges of maxtemp - mintemp
            location_ranges = list(map(
                lambda r: (
                    r["Location"],
                    float(r["MaxTemp"]) - float(r["MinTemp"])
                ),
                valid_rows
            ))

            # reduce to aggrete total temp range and row count per location
            def reducer(acc, item):
                loc, temp_range = item

                if loc not in acc:
                    acc[loc] = {"total": 0.0, "count": 0}

                acc[loc]["total"] += temp_range
                acc[loc]["count"] += 1
                return acc

            aggregated = reduce(reducer, location_ranges, {})

            # Calculate average temp range per location with aggregated totals and counts
            avg_ranges = {
                loc: values["total"] / values["count"]
                for loc, values in aggregated.items()
                if values["count"] > 0
            }

            # Sort and get top N locations from avg_ranges
            top = sorted(avg_ranges.items(), key=lambda x: x[1], reverse=True)[:self.top_n]

            # Convert to dict for plotting
            top_dict = dict(top)
            # 6️⃣ PLOT
            plt.figure(figsize=(10, 5))
            plt.bar(top_dict.keys(), top_dict.values())
            plt.title(f"Top {self.top_n} Locations by Avg Temp Range")
            plt.xlabel("Location")
            plt.ylabel("Average Temp Range (°C)")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(self.output_file)
            plt.close()

            print(f"\nChart saved to: {self.output_file}")

        except Exception as e:
            print(f"Error calculating temp range: {e}")