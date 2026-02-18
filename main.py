
from data_objects import DataStorageObject, DataLoader
from reports import ReportConfig, ReportGenerator
import logging
import sys
from pathlib import Path


#========================================= CLI LOGGING ARGS ===================================

VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def get_log_level_from_cli() -> int:
    """
    Read log level from sys.argv[1].
    Usage:
        python main.py            -> INFO
        python main.py DEBUG      -> DEBUG
        python main.py banana     -> prints error + exits
    """
    if len(sys.argv) == 1:
        return logging.INFO  # defaults to INFO type logging

    user_level = sys.argv[1].upper()

    if user_level not in VALID_LEVELS:
        print(f"Invalid log level: {sys.argv[1]}")
        print("Valid options:", ", ".join(sorted(VALID_LEVELS)))
        print("Example: python main.py DEBUG")
        sys.exit(1)

    return getattr(logging, user_level)


#========================================= LOGGING CONFIGURATION ===================================
def configure_logging(level: int) -> logging.Logger:
    logger = logging.getLogger("weather_app")
    logger.setLevel(level)

    
    if logger.handlers:
        return logger

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console output
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)

    # File output
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger


# ========================================= MAIN APPLICATION LOGIC ===================================
def main() -> None:
    level = get_log_level_from_cli()
    logger = configure_logging(level)

    logger.info("Application started...")
    logger.info(f"Log level set to {logging.getLevelName(level)}")

    try:
        data_loader = DataLoader()

        csv_path = "data/Weather Training Data.csv"
        logger.info(f"Loading CSV from: {csv_path}")

        df = data_loader.load_csv(csv_path)
        logger.info(f"CSV loaded successfully with {len(df)} rows and {len(df.columns)} columns")

        data_object = DataStorageObject(df)

        
        report_config = ReportConfig(preview_lines=10, summary_stats=True, average_rainfall=True, mean_rainfall_by_area=True, top_temp_range_by_area=True)

        report_generator = ReportGenerator(data_object, report_config)
        logger.info(f"Running report with config: {report_config}")
        report_generator.run_report()

        logger.info("Report completed successfully")
        logger.info("Application finished successfully")

        

    except Exception as e:
        logger.exception(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
