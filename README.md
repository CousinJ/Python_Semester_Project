
# Weather Project (Testing) - Module 5

## Design

I created the data_objects module to separate the reporting logic from the data logic. Fetching and storing data is soley in the hands of the Data_objects module now. Any further data manipulation/ refined analysis will be done by adding new methods to the DataStorageObject

In the Reports module, I used an abstract class to define ReportActions base class so I could build on more advanced reporting easily in the future by creating a new concrete ReportActions class and then modyfing the build_actions method in the Report Generator class. I use polymorphism here by allowing the report generator to use the method run_reports and iterate over the list of ReportActions and simply call the run method. I could have used Duck typing here and avoided using the abstract classes, but for me, this approach is much cleaner and simpler to modify in the future.

The ReportConfig @dataclass is used as a simple configuration class so I can save multiple reports in different variables by instantiating objects so I can avoid having to modify the code everytime I need to change the specif report/s.

I also added a logging system with command-line configuration. Users can enable or adjust logging behavior through CLI arguments, making debugging and tracing program execution much easier.

Robust exception handling is built into file loading, report execution, and data access to prevent crashes and provide meaningful error messages to the user.

main.py serves as a clean example of how all modules interact to produce a report.

Note: Naming may continue to evolve as the project grows and architecture stabilizes.

Note: It was hard to choose good names for these modules/classes early on into the Phases so I will be tweaking the names to of the modules and classes in the future.

## Overview

This project loads a weather dataset from Kaggle and processes it using pandas.
The program reads data from a CSV file into a pandas DataFrame, stores it inside a
custom object, and generates reports using advanced OOP principles such as:

Encapsulation (data stored privately inside a class)

Abstraction (report actions run through a common interface)

Polymorphism (different report actions share the same run() behavior)

Composition (ReportGenerator uses a DataStorageObject)

Dataclasses (configuration object for report settings)

Generators (lazy iteration over dataset rows)

Iterators (custom iterable data container)

Logging (runtime diagnostics and CLI control)

Exception handling (graceful failure and recovery)

This project is modularized into multiple modules so the classes can be reused
in later phases.


## Install dependencies

### pip install pandas 
### pip install matplotlib
### pip install pytest pytest-cov

---


**Note:**  You must download a dataset
separately and place it in your project folder to then use it. 

---

## Features

-- Data Loader object has methods to read CSV files and return a data frame
-- Data Storage Object stores the Data frame and a python list with getter functions to fetch data
-- Report generator generates reports based on the report config with individual configurable report classes

---

## Data Visualization (Module 6)

I created two new reports that use matplotlib to generate images in the "report_outputs" directory. 
The goal of these visualizations is to identify trends and compare weather characteristics across locations.

### MeanRainfallByArea
This report works by:

- Dropping NaN values for Location and Rainfall

- Grouping the data using pandas groupby

- Calculating the mean rainfall for each location

- Sorting the values and selecting the top N areas

- Plotting the results using a bar chart

I chose a bar graph because it makes comparing rainfall averages across multiple locations very clear and easy to interpret. You can quickly see which areas receive the most rainfall on average.



### TopTempRangeByLocation
    This report demonstrates functional programming techniques more explicitly.

Steps performed:

- Convert DataFrame rows to dictionaries

- Use filter() with a lambda to remove rows that contain NaN temperature values

- Use map() with a lambda to calculate temperature range (MaxTemp - MinTemp)

- Use reduce() to aggregate total range and count per location

- Compute average range per location

- Sort and select the top N locations

- Plot results using matplotlib

I chose a bar chart again here because it clearly shows which locations experience the largest average daily temperature swings.


### Tests


What I automated  (tests/test_reports.py):

- Test MeanRainfallByArea creates a plot file with valid data

- Test TopTempRangeByLocation creates a plot file with valid data

- Test TopTempRangeByLocation handles invalid data and does not genererate file





## Running tests

### run all tests
python -m pytest

### run tests with covereage
python -m pytest --cov=. --cov-report=term-missing

### run doctests only
python -m pytest --doctest-modules -vv
