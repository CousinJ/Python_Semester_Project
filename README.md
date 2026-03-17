# Weather Project – PySpark Migration (Module 8)

## Overview

This project processes a weather dataset from Kaggle and generates multiple reports using a modular, object-oriented design.

In this phase (Module 8), the application was migrated from a local pandas-based implementation to a **PySpark-based distributed system**, executed in a **virtual cluster environment using Google Colab**.

The goal of this migration was to demonstrate how an existing Python application can be adapted to run in a distributed data-processing environment.

---

## PySpark Environment

The application was executed using **Google Colab**, which served as a virtual PySpark cluster environment.


---

## Design

The project is structured into three main modules:

### data_objects.py

* Responsible for loading and storing data
* Uses a **PySpark DataFrame** instead of pandas
* Handles CSV validation and loading via `SparkSession`
* Encapsulates the dataset inside a `DataStorageObject`

### reports.py

* Contains all report logic using a modular design
* Uses an abstract base class (`ReportAction`) for extensibility
* Implements multiple concrete report classes such as:

  * PreviewLines
  * SummaryStats
  * AverageRainfall
  * MeanRainfallByArea
  * TopTempRangeByLocation
* Uses **PySpark transformations and aggregations** (`groupBy`, `agg`, `avg`)
* Uses matplotlib for visualization (after converting small aggregated results to pandas)

### main.py

* Entry point of the application
* Configures logging and handles execution flow
* Loads data using PySpark
* Runs reports based on a configurable `ReportConfig`

---

## Implementation

* Encapsulation (data stored inside a class)
* Abstraction (report actions share a common interface)
* Polymorphism (multiple report types use the same `run()` method)
* Composition (ReportGenerator uses DataStorageObject)
* Dataclasses (ReportConfig for flexible configuration)
* Logging (CLI-controlled logging levels)
* Exception Handling (robust error handling for file loading and execution)
* Distributed Computing (PySpark DataFrame operations)

---

## Changes for PySpark Migration

To adapt the project to run in a PySpark environment, the following changes were made:

* Replaced **pandas DataFrame** with **PySpark DataFrame**
* Updated CSV loading to use `spark.read.csv()`
* Removed:

  * threading-based report execution
  * multiprocessing logic
  * async CSV loading
  * row-by-row iteration (`iterrows`, generators)
* Replaced local data processing with **Spark transformations**:

  * `select()`
  * `filter()`
  * `groupBy()`
  * `agg()`
* Updated type hints and validation to expect PySpark DataFrames
* Modified logging and output handling to work with Spark actions like `.show()`



## Features

* Load CSV data using PySpark
* Generate multiple configurable reports
* Display preview and summary statistics
* Compute average rainfall using distributed aggregation
* Visualize:

  * Mean rainfall by location
  * Temperature range by location
* CLI-based logging configuration
* Modular and extensible architecture

---

## How to Run (Google Colab)

1. Open Google Colab
2. Install PySpark:

   ```python
   !pip install pyspark
   ```
3. Upload project files and dataset
4. Ensure CSV path is:

   ```python
   /content/data/Weather Training Data.csv
   ```
5. Run:

   ```python
   !python main.py
   ```



## Testing 

```bash
# run all tests
python -m pytest

# run with coverage
python -m pytest --cov=. --cov-report=term-missing

# run doctests
python -m pytest --doctest-modules -vv
```

---


