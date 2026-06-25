"""common.logging"""
from .custom_formatter import CustomFormatter
from .log import (
    log,
    debug,
    info,
    warn,
    error,
    error_stack_trace,
    initialize_logger,
    kill_logger
)
