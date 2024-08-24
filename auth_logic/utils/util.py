import os
import sys
from datetime import datetime

import yaml
from dateutil.parser import parse
from dotenv import dotenv_values

from auth_logic.usr_exceptions.error_handler import CustomError


class CommonUtils:
    def load_yaml(self, file_path: str) -> dict:
        """
        Load and return contents of a YAML file.
        """
        try:
            with open(file_path, "rb") as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise CustomError(e, sys) from e

    def now_time(self) -> str:
        """
        Get current time as a string.
        """
        return datetime.now().strftime("%H:%M:%S")

    def now_date(self) -> str:
        """
        Get current date as a string.
        """
        return datetime.now().date().isoformat()

    def time_diff_sec(self, future_dt: str, past_dt: str) -> float:
        """
        Calculate difference in seconds between two datetime strings.
        """
        f_dt = parse(future_dt)
        p_dt = parse(past_dt)
        return (f_dt - p_dt).total_seconds()

    def time_diff_ms(self, future_dt: str, past_dt: str) -> float:
        """
        Calculate difference in milliseconds between two datetime strings.
        """
        return self.time_diff_sec(future_dt, past_dt) * 1000

    def get_env_var(self, var_name: str) -> str:
        """
        Get environment variable value. Fallback to .env if not set.
        """
        return os.getenv(var_name, dotenv_values(".env").get(var_name, ""))
