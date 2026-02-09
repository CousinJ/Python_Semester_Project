import pytest
from data_objects import DataStorageObject, DataLoader
import pandas as pd

#test data_storage_object
def test_init_with_valid_dataframe():
   
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    obj = DataStorageObject(df)
    assert obj.df.equals(df)

def test_init_with_invalid_argument():
    with pytest.raises(ValueError):
        DataStorageObject(None)
    with pytest.raises(TypeError):
        DataStorageObject("not a dataframe")


#test data_storage_object methods
def test_iter_rows_dict():
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    obj = DataStorageObject(df)
    expected = [{'A': 1, 'B': 3}, {'A': 2, 'B': 4}]
    result = list(obj.iter_rows_dict())
    assert result == expected

def test_iter_dunder_method():
    df = pd.DataFrame([{"A": 1, "B": 2}])
    obj = DataStorageObject(df)

    it = iter(obj)  
    first = next(it)

    assert first == {"A": 1, "B": 2}

#test data loader

def test_load_csv_loads_dataframe():
    loader = DataLoader()
  

    df = loader.load_csv("tests/input_test.csv") 

    assert isinstance(df, pd.DataFrame)
    assert not df.empty 


def test_validate_csv_path_rejects_txt_file():
    loader = DataLoader()
    

    with pytest.raises(ValueError) as excinfo:
        loader.validate_csv_path("tests/input_test.txt")

    
    assert "Expected a .csv file" in str(excinfo.value)
