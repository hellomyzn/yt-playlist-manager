"""common.logging.logging"""
#########################################################
# Builtin packages
#########################################################
import sys
import io
import codecs
import traceback
import logging
from logging import handlers
from logging.handlers import RotatingFileHandler


#########################################################
# 3rd party packages
#########################################################

#########################################################
# Own packages
#########################################################
from common.config import Config
from common.log.custom_formatter import CustomFormatter


# Log format
LOG_FORMAT = "%(asctime)s %(levelname)-7s [%(process)d] [%(thread)d] [%(name)s] %(message)s [%(filename)s:%(funcName)s:%(lineno)d]"

LOG_DATE_FORMAT = None

# limitation of log file size(1Mb)
MAX_LOG_SIZE = 1 * 1024 * 1024

LOGGER = None

# log config
CONFIG = Config().config
LOG_NAME = CONFIG["LOG"]["NAME"]
LOG_PATH = CONFIG["LOG"]["PATH"]
LOG_LEVEL = CONFIG["LOG"]["LEVEL"]


def initialize_logger(log_name: str = LOG_NAME, log_file_path: str = LOG_PATH, level=LOG_LEVEL) -> None:
    """ Initialize global logge. generate logger with specific level and path.
    e.g.
        from common.logging import initialize_logger
        from common.logging import (
            info,
            error_stack_trace
        )
        initialize_logger("main", log_path, "info")
        info('log message')

    Args:
        log_name (str): Log name
        log_file_path (str): Output path
        level (Any): Log level

    Raises:
        Exception: when a log file path is wrong, it occurs
    """
    global LOGGER

    if LOGGER is not None:
        return

    LOGGER = logging.getLogger(log_name)
    formatter = CustomFormatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    try:
        # configure logger
        log_handler = RotatingFileHandler(
            log_file_path,
            mode="a",
            maxBytes=MAX_LOG_SIZE,
            backupCount=10,
            encoding="utf-8",
            delay=False)
        log_handler.setFormatter(formatter)
        LOGGER.addHandler(log_handler)

        # for console output
        if isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = codecs.getwriter("utf8")(sys.stdout.detach())

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        LOGGER.addHandler(stdout_handler)

        # set loglevel
        log_level = logging.getLevelName(level)
        if not isinstance(log_level, int):
            log_level = logging.INFO
        LOGGER.setLevel(log_level)

    except Exception as err:
        raise Exception("failed to initialize LOGGER") from err


def kill_logger():
    """Delete LOGGER"""
    global LOGGER
    if LOGGER is not None:
        name = LOGGER.name
        del logging.Logger.manager.loggerDict[name]

        # Close log file
        for handler in LOGGER.handlers:
            if isinstance(handlers, RotatingFileHandler):
                try:
                    handler.close()
                except Exception:
                    pass
    LOGGER = None


def log(level: int, format_str, *args):
    """Output log into a specific log file

    Args:
        level (int): Log level
        format_str (Any): Log format
        *args(tuple): Variable for format
    """
    if LOGGER is None:
        return
    try:
        # Convert messages and args into str
        if isinstance(format_str, str):
            message = format_str.format(*args)
        else:
            message = str(format_str)
        message = message.splitlines()
        log_str = ",".join(message)

        # Output to logfile
        LOGGER.log(level, log_str, stacklevel=3)
    except Exception as err:
        print(err)


def debug(format_str: str, *args):
    """Output debug log

    Args:
        format_str (str): Log format
        *args(tuple): Variable for format
    """
    log(logging.DEBUG, format_str, *args)


def info(format_str: str, *args):
    """Output info log

    Args:
        format_str (str): Log format
        *args(tuple): Variable for format
    """
    log(logging.INFO, format_str, *args)


def warn(format_str: str, *args):
    """Output warn log

    Args:
        format_str (str): Log format
        *args(tuple): Variable for format
    """
    log(logging.WARN, format_str, *args)


def warn_stack_trace(exception_obj):
    """Output stack trace(warn)

    Args:
        *exception_obj (Exception): Exception object
    """
    warn(f"stack trace output\n{exception_obj}\n", "".join(traceback.format_exc()))


def error(format_str: str, *args):
    """Output error log

    Args:
        format_str (str): Log format
        *args(tuple): Variable for format
    """
    log(logging.ERROR, format_str, *args)


def error_stack_trace(exception_obj):
    """Output stack trace(error)

    Args:
        *exception_obj (Exception): Exception object
    """
    error(f"stack trace output\n{exception_obj}\n", "".join(traceback.format_exc()))
