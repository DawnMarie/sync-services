from data_models.timecube import Timecube

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Sleep:

    title: str
    start_time: Timecube
    end_time: Timecube
    total_sleep: float  # in hours
    light_sleep: float  # in hours
    deep_sleep: float  # in hours
    rem_sleep: float  # in hours
    awake_time: float  # in hours
    resting_hr: int

    def format_hours_to_hm(cls, hours: float) -> str:
        """
        Convert hours (float) to a string formatted as "Xh YYYm"

        Args:
            hours: Float value representing hours

        Returns:
            String formatted as "Xh YYYm"
        """
        # Calculate total minutes
        total_minutes = round(hours * 60)

        # Calculate hours and remaining minutes
        h = total_minutes // 60
        m = total_minutes % 60

        # Format as "Xh YYYm"
        return f"{h}h {m}m"

    @classmethod
    def from_garmin_json(cls, garmin_response: dict) -> "Sleep":

        sleep_date = garmin_response.get('calendarDate', "Unknown Date")
        title = datetime.strptime(sleep_date, "%Y-%m-%d").strftime("%m.%d.%Y") if sleep_date else "Unknown"
        start_time = Timecube.from_timestamp(int(garmin_response.get('sleepStartTimestampGMT')/1000), 'GMT')
        end_time = Timecube.from_timestamp(int(garmin_response.get('sleepEndTimestampGMT')/1000), 'GMT')
        total_sleep = round(
            sum((garmin_response.get(k, 0) or 0) for k in ['deepSleepSeconds', 'lightSleepSeconds', 'remSleepSeconds']) / 3600, 1)
        light_sleep = round(garmin_response.get('lightSleepSeconds', 0) / 3600, 1)
        deep_sleep = round(garmin_response.get('deepSleepSeconds', 0) / 3600, 1)
        rem_sleep = round(garmin_response.get('remSleepSeconds', 0) / 3600, 1)
        awake_time = round(garmin_response.get('awakeSleepSeconds', 0) / 3600, 1)
        resting_hr = 0

        return cls(
            title=title,
            start_time=start_time,
            end_time=end_time,
            total_sleep=total_sleep,
            light_sleep=light_sleep,
            deep_sleep=deep_sleep,
            rem_sleep=rem_sleep,
            awake_time=awake_time,
            resting_hr=resting_hr
        )

