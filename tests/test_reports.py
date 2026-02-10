from reports import ReportGenerator, ReportConfig, ReportAction
from data_objects import DataStorageObject
import pandas as pd
import pytest   



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