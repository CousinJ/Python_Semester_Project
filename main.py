from data_objects import DataStorageObject, DataLoader
from reports import ReportConfig, ReportGenerator 
    

def main():

    data_loader = DataLoader()

    df = data_loader.load_csv('data/Weather Training Data.csv')

    data_object = DataStorageObject(df)

    report_config = ReportConfig(preview_lines=10, summary_stats=True, show_row_count=True)

    report_generator = ReportGenerator(data_object, report_config)
    report_generator.run_report()

if __name__ == "__main__":
    main()