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
import threading
import multiprocessing as mp

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



    def run_report_threaded(self) -> None:
        """
        Run report actions concurrently using  threading.Thread.

        NOTE:
        - This gives concurrency (actions overlap).
        - It may not speed up CPU-heavy work in CPython due to the GIL.
        - If multiple actions use matplotlib at the same time, it can be unstable.
        """
        self.build_actions()

        exceptions = []
        #use array to store non plot reports
        non_plot_reports = []
        plot_reports = []
        lock = threading.Lock()

        # separate plot and mp reports to avoid matplotlib concurrency issues and multiprocessing inside thread
        #run these plot/mp reports sequentially
        for action in self.report_actions:
            if getattr(action, "is_plot", False) or getattr(action, "uses_multiprocessing", False):
                plot_reports.append(action)       
            else:
                non_plot_reports.append(action)   


        def worker(action):
            try:
                action.run(self.data_utility)
            except Exception as e:
                # store exceptions thread-safely
                with lock:
                    exceptions.append((type(action).__name__, e))

        threads = []
        for action in non_plot_reports:
            t = threading.Thread(target=worker, args=(action,))
            t.start()
            threads.append(t)

        

        # Wait for all report actions to finish
        for t in threads:
            t.join()

        # If any thread failed, raise one combined error
        if exceptions:
            msg_lines = ["One or more report actions failed:"]
            for name, e in exceptions:
                msg_lines.append(f"- {name}: {e}")
            raise RuntimeError("\n".join(msg_lines))
        
        # Run plot reports sequentially to avoid matplotlib issues
        for action in plot_reports:
            try:
                action.run(self.data_utility)
            except Exception as e:
                print(f"Error in plot report {type(action).__name__}: {e}")





class ReportAction(ABC):

    """
    Abstract base class for report actions.
    """
    def __init__(self) -> None:
        self.is_plot = False

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
        super().__init__()

    def run(self, data) -> None:
        print(data.df.head(self.num_lines))


class SummaryStats(ReportAction):
    """
    Concrete ReportAction class to show summary statistics from the DataStorageObject.
    """
    def __init__(self):
        super().__init__()
    def run(self, data) -> None:
        print(data.df.describe())

class AverageRainfall(ReportAction):
    """
    Average rainfall using multiprocessing (multi-core parallelism).
    """

    def __init__(self, processes: int | None = None, chunks_per_process: int = 4):
        super().__init__()
        self.uses_multiprocessing = True
        self.processes = processes
        self.chunks_per_process = chunks_per_process

    @staticmethod
    def _sum_count_rainfall(chunk: list[float]) -> tuple[float, int]:
        """
        Multiprocessing worker: returns (sum, count) for a chunk.
        Must be staticmethod (picklable) for Windows spawn.
        """
        total = 0.0
        count = 0
        for v in chunk:
            total += v
            count += 1
        return total, count

    def run(self, data) -> None:
        # Get Rainfall column
        s = data.df.get("Rainfall")
        if s is None:
            print("Avg Rainfall: N/A (Rainfall column missing)")
            return

        # Clean values to floats, drop NaNs, make plain list for pickling
        cleaned = pandas.to_numeric(s, errors="coerce").dropna().tolist()
        if not cleaned:
            print("Avg Rainfall: N/A")
            return

        cpu = mp.cpu_count()
        proc = self.processes or cpu

        # Chunk data
        num_chunks = max(proc * self.chunks_per_process, 1)
        chunk_size = max(len(cleaned) // num_chunks, 1)
        chunks = [cleaned[i:i + chunk_size] for i in range(0, len(cleaned), chunk_size)]

        # Windows-safe: use spawn context explicitly
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=proc) as pool:
            results = pool.map(AverageRainfall._sum_count_rainfall, chunks)

        total = sum(t for t, _ in results)
        count = sum(c for _, c in results)

        print("Avg Rainfall:", total / count if count else "N/A")




#plot mean rainfall for each area
class MeanRainfallByArea(ReportAction):
    """
    Concrete ReportAction class to show mean rainfall by area from the DataStorageObject using Matplotlib, generates file into "report_outputs" dir.
    """
    def __init__(self, top_n: int = 15, output_file: str = "report_outputs/Mean_Rainfall_By_Area.png"):
        super().__init__()
        self.top_n = top_n
        self.output_file = output_file
        self.is_plot = True

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
        super().__init__()
        self.is_plot = True
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