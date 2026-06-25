"""common.logging.custom_formatter"""
#########################################################
# Builtin packages
#########################################################
import logging
import time

#########################################################
# 3rd party packages
#########################################################

#########################################################
# Own packages
#########################################################

LOG_DATE_FORMAT_BASE = "%Y-%m-%dT%H:%M:%S"
LOG_DATE_FORMAT_TIMEZONE = "%z"


class CustomFormatter(logging.Formatter):
    """CustomFormatter"""

    def formatTime(self, record, datefmt=None) -> str:
        """to override a formatTime method

        - has datefmt    : follow format as datefmt
        - not has datefmt: follow format as LOG_DATE_FORMAT_BASE

        Args:
            record (any): record
            datefmt (str, optional): date format, default is None

        Returns:
            str: date data
        """
        result = ""
        cvt = self.converter(record.created)
        if datefmt:
            result = time.strftime(datefmt, cvt)
        else:
            time_strftime = time.strftime(LOG_DATE_FORMAT_BASE, cvt)
            time_zone = time.strftime(LOG_DATE_FORMAT_TIMEZONE, cvt)
            result = "%s.%03d%s" % (time_strftime, record.msecs, time_zone)

        return result
