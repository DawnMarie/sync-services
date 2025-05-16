from data_models.timecube import Timecube

from dataclasses import dataclass

@dataclass
class PR:

    activity_date: Timecube
    activity_type: str
    activity_name: str
    type_id: int
    value: str
    pace: str
    icon: str

    @staticmethod
    def _format_activity_type(activity_type) -> str:
        if activity_type is None:
            return "Walking"
        return activity_type.replace('_', ' ').title()

    @staticmethod
    def _replace_activity_name_by_type_id(type_id):
        type_id_name_map = {
            1: "1K",
            2: "1mi",
            3: "5K",
            4: "10K",
            7: "Longest Run",
            8: "Longest Ride",
            9: "Total Ascent",
            10: "Max Avg Power (20 min)",
            12: "Most Steps in a Day",
            13: "Most Steps in a Week",
            14: "Most Steps in a Month",
            15: "Longest Goal Streak"
        }
        return type_id_name_map.get(type_id, "Unnamed Activity")

    @staticmethod
    def _format_garmin_value(value, type_id):
        if type_id == 1:  # 1K
            total_seconds = round(value)  # Round to the nearest second
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            formatted_value = f"{minutes}:{seconds:02d} /km"
            pace = formatted_value  # For these types, the value is the pace
            icon = "🥇"
            return formatted_value, pace, icon

        if type_id == 2:  # 1mile
            total_seconds = round(value)  # Round to the nearest second
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            formatted_value = f"{minutes}:{seconds:02d}"
            total_pace_seconds = total_seconds / 1.60934  # Divide by 1.60934 to get pace per km
            pace_minutes = int(total_pace_seconds // 60)  # Convert to integer
            pace_seconds = int(total_pace_seconds % 60)  # Convert to integer
            formatted_pace = f"{pace_minutes}:{pace_seconds:02d} /km"
            icon = "⚡"
            return formatted_value, formatted_pace, icon

        if type_id == 3:  # 5K
            total_seconds = round(value)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            formatted_value = f"{minutes}:{seconds:02d}"
            total_pace_seconds = total_seconds // 5  # Divide by 5km
            pace_minutes = total_pace_seconds // 60
            pace_seconds = total_pace_seconds % 60
            formatted_pace = f"{pace_minutes}:{pace_seconds:02d} /km"
            icon = "👟"
            return formatted_value, formatted_pace, icon

        if type_id == 4:  # 10K
            # Round to the nearest second
            total_seconds = round(value)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            if hours > 0:
                formatted_value = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                formatted_value = f"{minutes}:{seconds:02d}"
            total_pace_seconds = total_seconds // 10  # Divide by 10km
            pace_minutes = (total_pace_seconds % 3600) // 60
            pace_seconds = total_pace_seconds % 60
            formatted_pace = f"{pace_minutes}:{pace_seconds:02d} /km"
            icon = "⭐"
            return formatted_value, formatted_pace, icon

        if type_id in [7, 8]:  # Longest Run, Longest Ride
            value_km = value / 1000
            formatted_value = f"{value_km:.2f} km"
            pace = ""  # No pace for these types
            icon = ""
            if type_id == 7:
                icon = "🏃"
            if type_id == 8:
                icon = "🚴"
            return formatted_value, pace, icon

        if type_id == 9:  # Total Ascent
            value_m = int(value)
            formatted_value = f"{value_m:,} m"
            pace = ""
            icon = "🚵"
            return formatted_value, pace, icon

        if type_id == 10:  # Max Avg Power
            value_w = round(value)
            formatted_value = f"{value_w} W"
            pace = ""
            icon = "🔋"
            return formatted_value, pace, icon

        if type_id in [12, 13, 14]:  # Step counts
            value_steps = round(value)
            formatted_value = f"{value_steps:,}"
            pace = ""
            icon = ""
            if type_id == 12:
                icon = "👣"
            if type_id == 13:
                icon = "🚶"
            if type_id == 14:
                icon = "📅"
            return formatted_value, pace, icon

        if type_id == 15:  # Longest Goal Streak
            value_days = round(value)
            formatted_value = f"{value_days} days"
            pace = ""
            icon = "✔️"
            return formatted_value, pace, icon

        # Default case
        if int(value // 60) < 60:  # If the total time is less than an hour
            minutes = int(value // 60)
            seconds = round((value / 60 - minutes) * 60, 2)
            formatted_value = f"{minutes}:{seconds:05.2f}"
        else:  # If total time is one hour or more
            hours = int(value // 3600)
            minutes = int((value % 3600) // 60)
            seconds = round(value % 60, 2)
            formatted_value = f"{hours}:{minutes:02}:{seconds:05.2f}"

        pace = ""
        icon = "🏅"
        return formatted_value, pace, icon

    @classmethod
    def from_garmin_json(cls, garmin_response: dict) -> "PR":
        timecube = Timecube.from_date_time_string(garmin_response.get('prStartTimeGmtFormatted'))
        activity_type = cls._format_activity_type(garmin_response.get('activityType'))
        type_id = garmin_response.get('typeId', 0)
        value, pace, icon = cls._format_garmin_value(garmin_response.get('value', 0), type_id)

        return cls(
            activity_date=timecube,
            activity_type=activity_type,
            activity_name=cls._replace_activity_name_by_type_id(garmin_response.get('typeId')),
            type_id=type_id,
            value=value,
            pace=pace,
            icon=icon
        )
