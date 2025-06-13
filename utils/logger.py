import logging
import os
import sys
from datetime import datetime


def error_message_details(error, error_detail: sys) -> str:
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = "Error Occurred in python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name, line_number, str(error)
    )
    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_details(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        return self.error_message


ROOT_DIR = os.getcwd()
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


LOG_FILE = f'{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log'
LOG_FILE_PATH = os.path.join(LOGS_DIR, LOG_FILE)


logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

