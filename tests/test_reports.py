from importlib.abc import Loader
from reports import ReportGenerator, ReportConfig, ReportAction, TopTempRangeByLocation, MeanRainfallByArea
from data_objects import DataStorageObject, DataLoader
import pandas as pd
import pytest   
import matplotlib 
matplotlib.use('Agg')  # Use non-interactive backend for testing



def test_report_generator_init_with_valid_arguments():
    df = DataStorageObject(pd.DataFrame({'A': [1, 2], 'B': [3, 4]}))
    config = ReportConfig(preview_lines=5, summary_stats=True, average_rainfall=False)
    report_gen = ReportGenerator(df, config)

    assert report_gen.data_utility == df
    assert report_gen.config == config
    assert report_gen.report_actions == []


def test_report_generator_init_with_invalid_arguments_data_object():
    df = [1,2,3,4,5,6]
    config = ReportConfig(preview_lines=5, summary_stats=True, average_rainfall=False)
    

    with pytest.raises(TypeError, match="data_object must be an instance of DataStorageObject"):
        report_gen = ReportGenerator(df, config)



def test_report_generator_init_with_invalid_arguments_report_config():
    df = DataStorageObject(pd.DataFrame({'A': [1, 2], 'B': [3, 4]}))
    config ={'lines': 5, 'summary_stats': True, 'average_rainfall': False}
    

    with pytest.raises(TypeError, match="config must be an instance of ReportConfig"):
        report_gen = ReportGenerator(df, config)



def test_report_generator_build_actions_building_correctly():
    df = DataStorageObject(pd.DataFrame({'A': [1, 2], 'B': [3, 4]}))
    config = ReportConfig(preview_lines=5, summary_stats=True, average_rainfall=False)
    report_gen = ReportGenerator(df, config)

    report_gen.build_actions()

    assert len(report_gen.report_actions) == 2
    assert all(isinstance(action, ReportAction) for action in report_gen.report_actions)


# ================================================    Report Actions Tests  ================================================

def test_mean_rainfall_by_area_creates_plot_file(tmp_path):
    df = pd.DataFrame({
        "Location": ["A", "A", "B", "B"],
        "Rainfall": [100.0, 150.0, 200.0, 180.0]
    })
    dso = DataStorageObject(df)

    out_file = tmp_path / "mean_rain.png"
    report = MeanRainfallByArea(top_n=2, output_file=str(out_file))
    report.run(dso)

    assert out_file.exists()
    assert out_file.stat().st_size > 0 

def test_top_temp_range_by_location_creates_plot_file(tmp_path):
    df = pd.DataFrame({
        "Location": ["A", "A", "B", "B"],
        "MinTemp": [10.0, 5.0, 0.0, 2.0],
        "MaxTemp": [20.0, 25.0, 10.0, 12.0],
    })
    dso = DataStorageObject(df)

    out_file = tmp_path / "temp_range.png"
    report = TopTempRangeByLocation(top_n=2, output_file=str(out_file))
    report.run(dso)

    assert out_file.exists()
    assert out_file.stat().st_size > 0

def test_top_temp_range_handles_no_valid_rows(capsys, tmp_path):
    
    df = pd.DataFrame({"Location": ["A"], "MinTemp": [None], "MaxTemp": [None]})
    dso = DataStorageObject(df)

    out_file = tmp_path / "temp_range.png"
    report = TopTempRangeByLocation(top_n=2, output_file=str(out_file))
    report.run(dso)

    out = capsys.readouterr().out
    assert "No valid temperature rows found." in out
    assert not out_file.exists()  