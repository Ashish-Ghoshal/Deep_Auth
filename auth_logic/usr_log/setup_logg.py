import logging
import os
from datetime import datetime

LOG_DIRECTORY = "log_files"
LOG_DIRECTORY = os.path.join(os.getcwd(), LOG_DIRECTORY)

os.makedirs(LOG_DIRECTORY, exist_ok=True)

CURRENT_TIMESTAMP = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
log_file_name = f"logging_file_{CURRENT_TIMESTAMP}.log"

log_file_path = os.path.join(LOG_DIRECTORY, log_file_name)

logging.basicConfig(
    filename=log_file_path,
    filemode="w",
    format="[%(asctime)s] %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger("AuthLog")

extra_logger = logging.getLogger("ExtraLog")
secondary_logger = logging.getLogger("SecondaryLog")

def demo_log_levels():
    logger.debug("Debugging mode activated.")
    logger.info("Informational message logged.")
    logger.warning("Warning detected!")
    logger.error("An error has occurred!")
    logger.critical("Critical issue encountered!")

def redundant_logger_example():
    secondary_logger.info("This is an extra logging function.")
