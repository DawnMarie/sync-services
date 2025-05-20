"""Object to contain all the necessary time formats"""

from datetime import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo


@dataclass()
class Timecube:
    """
    Contains a date/time object with the following formats:
    today = string of format '%Y-%m-%d'
    today_time = string of format "%Y-%m-%dT%H:%M:%S.000Z"
    today_epoch = int of the Unix epoch time in ms
    today_timestamp = int of the Unix epoch time in s
    timezone = local_tz of the timecube
    week_number = the number of the week containing the date in the timecube
    """

    _dt_utc: datetime
    local_tz: str = "America/New_York"

    def __init__(self, _dt_utc: datetime = None, local_tz: str = "America/New_York"):
        if _dt_utc is None:
            _dt_utc = datetime.now(tz=ZoneInfo("UTC"))
        self._dt_utc = _dt_utc
        self.local_tz = local_tz

    @classmethod
    def from_Y_m_d_H_M_S(cls, date_str: str, local_tz: str = "America/New_York"):
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return cls._build(dt, local_tz)

    @classmethod
    def from_Y_m_d(cls, date_str: str, local_tz: str = "America/New_York"):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return cls._build(dt, local_tz)

    @classmethod
    def from_date_time_string(cls, date_time_str: str, local_tz: str = "America/New_York"):
        try:
            # Try to parse the ISO format with a timezone offset
            if '+' in date_time_str or '-' in date_time_str[10:]:  # Check for timezone offset after the date portion
                # Remove the timezone offset as we'll handle timezone conversion separately
                dt_str = date_time_str[:-6]  # Remove the +00:00 part
                dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                try:
                    # Try the format with fractional seconds
                    dt = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    try:
                        # Try format without fractional seconds
                        dt = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        try:
                            # Try a space-separated format
                            dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                dt = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.000Z")
                            except ValueError:
                                try:
                                    # Try a simple date format
                                    dt = datetime.strptime(date_time_str, "%Y-%m-%d")
                                except ValueError:
                                    raise ValueError(f"Time data '{date_time_str}' doesn't match any expected formats")
        except Exception as e:
            raise ValueError(f"Error parsing date time string '{date_time_str}': {str(e)}")
        return cls._build(dt, local_tz)
    @classmethod
    def from_date(cls, year: int, month: int, day: int, local_tz: str = "America/New_York"):
        dt = datetime(year=year, month=month, day=day, tzinfo=ZoneInfo(local_tz))
        return cls._build(dt, local_tz)

    @classmethod
    def from_datetime(cls, dt: datetime):
        if not dt.tzinfo:
            return cls._build(dt, "America/New_York")
        if isinstance(dt.tzinfo, ZoneInfo):
            ##TODO: Figure out how to get a timezone name that isn't EDT
            return cls._build(dt, "America/New_York")
        return cls._build(dt, "UTC")

    @classmethod
    def from_epoch(cls, epoch: int, local_tz: str = "America/New_York"):
        dt = datetime.fromtimestamp(epoch / 1000, tz=ZoneInfo("UTC"))
        return cls._build(dt, local_tz)

    @classmethod
    def from_timestamp(cls, timestamp: int, local_tz: str = "America/New_York"):
        dt = datetime.fromtimestamp(timestamp)
        return cls._build(dt, local_tz)

    @classmethod
    def _build(cls, dt: datetime, local_tz: str):
        # If datetime has no timezone, assume it's in the target local timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(local_tz))
            # Convert to UTC for storage
            dt = dt.astimezone(ZoneInfo("UTC"))
        else:
            # If datetime has a timezone, convert to UTC for storage
            dt = dt.astimezone(ZoneInfo("UTC"))
        return cls(_dt_utc=dt, local_tz=local_tz)

    def _localized_dt(self) -> datetime:
        return self._dt_utc.astimezone(ZoneInfo(self.local_tz))

    def set_local_tz(self, new_local_tz: str):
        self.local_tz = new_local_tz

    @property
    def date_for_titles(self) -> str:
        return self._localized_dt().strftime('%Y.%m.%d')

    @property
    def date_Y_m_d(self) -> str:
        return self._localized_dt().strftime('%Y-%m-%d')

    @property
    def date_time_Y_m_d_H_M_S(self) -> str:
        return self._dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    @property
    def clock_time_H_M(self) -> str:
        return self._localized_dt().strftime("%H:%M")

    @property
    def date_in_ms(self) -> int:
        return int(self._localized_dt().timestamp() * 1000)

    @property
    def date_in_s(self) -> int:
        return int(self._localized_dt().timestamp())

    @property
    def date_in_datetime(self) -> datetime:
        return self._localized_dt()

    @property
    def week_number(self) -> str:
        return self._localized_dt().strftime("%V")

    @property
    def date_M_Y(self):
        return self._localized_dt().strftime("%B %Y")

    @property
    def date_only_if_time_is_midnight(self) -> str:
        """Format date based on whether the time is midnight or not"""
        is_midnight = self.date_in_datetime.hour == 0 and self.date_in_datetime.minute == 0 and self.date_in_datetime.second == 0

        if is_midnight:
            return self.date_Y_m_d
        else:
            return self.date_time_Y_m_d_H_M_S