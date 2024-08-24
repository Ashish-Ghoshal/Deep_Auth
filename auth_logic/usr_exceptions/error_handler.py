import sys
import logging

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("ErrorHandler")

class CustomError(Exception):
    def __init__(self, error_message: Exception, error_details: sys):
        super().__init__(error_message)
        self.error_msg = self.generate_error_message(error_message, error_details)

    @staticmethod
    def generate_error_message(error: Exception, error_details: sys) -> str:
        _, _, trace = error_details.exc_info()
        file_name = trace.tb_frame.f_code.co_filename
        log.error(f"Error in {file_name} at line {trace.tb_lineno}: {error}")
        return f"Critical issue in [{file_name}], at line [{trace.tb_lineno}]: {error}."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.error_msg}"

    def __str__(self) -> str:
        return self.error_msg

    def log_exception(self):
        log.exception(f"Exception raised: {self.error_msg}")

    def raise_custom_error(self):
        log.critical("A critical custom error is being raised!")
        raise self

def handle_generic_error(error_msg: str):
    log.error(f"Generic error: {error_msg}")
