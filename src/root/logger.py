import sys
from functools import wraps
import traceback
from typing import Callable
from fastapi import Request
import logging
import os
from fastapi.responses import JSONResponse
import json_log_formatter
from logging.handlers import RotatingFileHandler
from datetime import datetime
import asyncio

json_formater = json_log_formatter.VerboseJSONFormatter(
    fmt="[%(levelname)s | %(module)s | L%(lineno)d | %(pathname)s] %(asctime)s: %(message)s ",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

# ErrorLogger
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y')}.log"
logs_path = os.path.join(os.getcwd(), "logs", LOG_FILE)
os.makedirs(logs_path, exist_ok=True)
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.WARNING)
handler1 = logging.FileHandler(LOG_FILE_PATH, mode="a")
handler1.setLevel(logging.WARNING)
handler1.setFormatter(json_formater)
error_logger.addHandler(handler1)


# information logger
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y')}.log"
logs_path = os.path.join(os.getcwd(), "infologs", LOG_FILE)
os.makedirs(logs_path, exist_ok=True)
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

info_logger = logging.getLogger("info_logger")
info_logger.setLevel(logging.INFO)
handler2 = logging.FileHandler(LOG_FILE_PATH, mode="a")
handler2.setLevel(logging.INFO)
handler2.setFormatter(json_formater)
info_logger.addHandler(handler2)


# time data logger
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y')}.log"
logs_path = os.path.join(os.getcwd(), "timelogs", LOG_FILE)
os.makedirs(logs_path, exist_ok=True)
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

time_logger = logging.getLogger("time_logger")
time_logger.setLevel(logging.INFO)
handler3 = RotatingFileHandler(filename=LOG_FILE_PATH, maxBytes=1000000, backupCount=5)
handler3.setLevel(logging.INFO)
handler3.setFormatter(json_formater)
time_logger.addHandler(handler3)


# payment logger
LOG_FILE = f"payment.log"
payment_logger = logging.getLogger("payment_logger")
logs_path = os.path.join(os.getcwd(), "payment_logs", LOG_FILE)
handler4 = RotatingFileHandler(filename=LOG_FILE_PATH, maxBytes=1000000, backupCount=5)
handler4.setLevel(logging.INFO)
handler4.setFormatter(json_formater)
payment_logger.addHandler(handler4)


async def log_to_file(error_message: Exception, request: Request, event_id: str):
    """_summary_
    This Functions logs the error message asynchronously returned by
    the caller function

    Args:
        error_message (Exception): Error Message
        request (Request): Async request Object
        func (Callable): Caller Function wrapper
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    # Extract the filename and line number from the traceback
    if exc_traceback is not None:
        tb = traceback.extract_tb(exc_traceback)[-1]
        filename, line_number, func_name, text = tb
        error_logger.error(
            {
                "event_id": event_id,
                "message": f"Route:{request.url}, error:{error_message}",
                "Filename": filename,
                "line number": line_number,
                "function name": func_name,
            }
        )
    else:
        error_logger.error(
            {
                "event_id": event_id,
                "message": f"Route:{request.url}, error:{error_message}",
            }
        )


def log_route(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        try:
            # checking for the request parameter in route
            request = kwargs["request"]

        except KeyError as e:
            logger.error({f"Filename:{func.__code__.co_filename}, error:{e}"})
            return JSONResponse(
                status_code=500, content="Request Parameter Not Found in Route"
            )

        try:
            response = await func(*args, **kwargs)
        except Exception as e:
            asyncio.create_task(
                log_to_file(
                    error_message=e, request=request, event_id="default_event_id"
                )
            )
            sys.stdout.write(str(e))

            raise e

        return response

    return wrapper
