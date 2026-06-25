"""utils.datetime_parser"""
#########################################################
# Builtin packages
#########################################################
import re
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################


@dataclass
class DatetimeParser(object):
    """class to decode and encode"""
    FORMAT_PATTERN = re.compile(r".*Z$")

    @classmethod
    def encode_to_iso_format(cls, datetime_: datetime | None = None) -> str | None:
        """convert from datetime to str (iso format: YYYY-MM-DDThh:mm:ss.fff+09:00)

        Args:
            datetime_ (datetime | None, optional): datetime. Defaults to None.

        Returns:
            str | None: datetime string formatted by ISO
        """
        if datetime_ is None:
            return None
        return datetime_.astimezone().isoformat(timespec="milliseconds")

    @classmethod
    def decode_from_iso_format(cls, datetime_: str | None = None) -> datetime | None:
        """convert from str (iso format: YYYY-MM-DDThh:mm:ss.fff+00:00) to datetime

        Args:
            datetime_ (str | None, optional): datetime string iso formatted. Defaults to None.

        Returns:
            datetime | None: datetime
        """
        if datetime_ is None:
            return None

        datetime_ = datetime_.strip()

        # replace datetime format from Z to +00:00
        if cls.FORMAT_PATTERN.match(datetime_):
            datetime_ = datetime_.replace("Z", "+09:00")

        # e.g.
        #   datetime_ = "2024-03-22T07:00:00.000+00:00"
        #   yy_mm_dd_hh_mm_ss = "2024-03-22T07:00:00"
        #   time_zone = "+00:00"
        #   fraction = ".000"
        yy_mm_dd_hh_mm_ss = datetime_[:19]
        time_zone = ""
        fraction = datetime_[:19]
        if fraction.find("+") != -1 or fraction.find("-") != -1:
            time_zone = datetime_[-6:]
            fraction = datetime_[19:-6]

        datetime_ = yy_mm_dd_hh_mm_ss + fraction + time_zone

        return datetime.fromisoformat(datetime_).astimezone()

    @classmethod
    def decode_from_str_date(cls, datetime_: str | None = None) -> datetime | None:
        """convert from str date(YYYY-MM-DD) to datetime

        Args:
            datetime_ (str | None, optional): only date (YYYY-MM-DD). Defaults to None.

        Returns:
            datetime | None: datetime
        """
        if datetime_ is None:
            return None

        datetime_ = datetime_.strip()

        # validate datetime
        if len(datetime_) != 10 or datetime_.find("-") == -1:
            return None

        year, month, day = datetime_.split("-")
        time_zone = ZoneInfo("Asia/Tokyo")
        dt = datetime(int(year), int(month), int(day), tzinfo=time_zone)
        return dt

    @classmethod
    def encode_to_unix_timestamp(cls, datetime_: datetime | None = None) -> int | None:
        """convert from datetime to unix timestamp (e.g. 1709218800)

        Args:
            datetime_ (datetime | None, optional): datetime. Defaults to None.

        Returns:
            int | None: unix timestamp (e.g. 1709218800)
        """
        if datetime_ is None:
            return None
        return int(datetime_.replace().timestamp())
