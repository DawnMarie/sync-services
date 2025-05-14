from data_models.timecube import Timecube

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Activity:

    icon: Optional[str]
    activity_date: Timecube
    avg_power: Optional[int]
    max_power: Optional[int]
    title: str = ""
    type: str = ""
    subtype: str = ""
    distance: float = 0  # in miles
    duration: int = 0  # in minutes
    cals_burned: int = 0
    avg_pace: str = ""
    training_effect: str = ""
    aerobic: int = 0
    aerobic_effect: str = ""
    anaerobic: int = 0
    anaerobic_effect: str = ""
    pr: bool = False
    fav: bool = False

    ACTIVITY_ICONS = {
        "Barre": "https://img.icons8.com/?size=100&id=66924&format=png&color=9A6DD7",
        "Breathwork": "https://img.icons8.com/?size=100&id=9798&format=png&color=9A6DD7",
        "Cardio": "https://img.icons8.com/?size=100&id=71221&format=png&color=9A6DD7",
        "Cycling": "https://img.icons8.com/?size=100&id=47443&format=png&color=9A6DD7",
        "HIIT": "https://img.icons8.com/?size=100&id=5yT8ndkVJsyV&format=png&color=9A6DD7",
        "Hiking": "https://img.icons8.com/?size=100&id=9844&format=png&color=9A6DD7",
        "Indoor Cardio": "https://img.icons8.com/?size=100&id=62779&format=png&color=9A6DD7",
        "Indoor Cycling": "https://img.icons8.com/?size=100&id=47443&format=png&color=9A6DD7",
        "Indoor Rowing": "https://img.icons8.com/?size=100&id=71098&format=png&color=9A6DD7",
        "Pilates": "https://img.icons8.com/?size=100&id=9774&format=png&color=9A6DD7",
        "Meditation": "https://img.icons8.com/?size=100&id=9798&format=png&color=9A6DD7",
        "Rowing": "https://img.icons8.com/?size=100&id=71491&format=png&color=9A6DD7",
        "Running": "https://img.icons8.com/?size=100&id=k1l1XFkME39t&format=png&color=9A6DD7",
        "Strength Training": "https://img.icons8.com/?size=100&id=107640&format=png&color=9A6DD7",
        "Stretching": "https://img.icons8.com/?size=100&id=djfOcRn1m_kh&format=png&color=9A6DD7",
        "Swimming": "https://img.icons8.com/?size=100&id=9777&format=png&color=9A6DD7",
        "Trail Running": "https://img.icons8.com/?size=100&id=k1l1XFkME39t&format=png&color=9A6DD7",
        "Treadmill Running": "https://img.icons8.com/?size=100&id=9794&format=png&color=9A6DD7",
        "Walking": "https://img.icons8.com/?size=100&id=9807&format=png&color=9A6DD7",
        "Yoga": "https://img.icons8.com/?size=100&id=9783&format=png&color=9A6DD7",
        # Add more mappings as needed
    }

    @staticmethod
    def _format_activity_type(activity_type: str, activity_name=""):
        # First, format the activity type as before
        formatted_type = activity_type.replace('_', ' ').title() if activity_type else "Unknown"

        # Initialize the subtype as the same as the main type
        activity_subtype = formatted_type
        activity_type = formatted_type

        # Map of specific subtypes to their main types
        activity_mapping = {
            "Barre": "Strength",
            "Indoor Cardio": "Cardio",
            "Indoor Cycling": "Cycling",
            "Indoor Rowing": "Rowing",
            "Speed Walking": "Walking",
            "Strength Training": "Strength",
            "Trail Running": "Running",
            "Treadmill Running": "Running"
        }

        # Special replacement for Rowing V2
        if formatted_type == "Rowing V2":
            activity_type = "Rowing"

        # Special case for Yoga and Pilates
        elif formatted_type in ["Yoga", "Pilates"]:
            activity_type = "Yoga/Pilates"
            activity_subtype = formatted_type

        # If the formatted type is in our mapping, update both the main type and subtype
        if formatted_type in activity_mapping:
            activity_type = activity_mapping[formatted_type]
            activity_subtype = formatted_type

        # Special cases for activity names
        if activity_name and "meditation" in activity_name.lower():
            return "Meditation", "Meditation"
        if activity_name and "barre" in activity_name.lower():
            return "Strength", "Barre"
        if activity_name and "stretch" in activity_name.lower():
            return "Stretching", "Stretching"

        if activity_type == "Hiit":
            activity_type = "HIIT"
            activity_subtype = "HIIT"

        return activity_type, activity_subtype

    @staticmethod
    def _format_pace(average_speed_from_garmin):
        if average_speed_from_garmin > 0:
            pace_min_mile = 1609.34 / (average_speed_from_garmin * 60)  # Convert to min/mile
            minutes = int(pace_min_mile)
            seconds = int((pace_min_mile - minutes) * 60)
            return f"{minutes}:{seconds:02d} min/mile"
        else:
            return ""

    @staticmethod
    def _format_training_message(message):
        messages = {
            'NO_': 'No Benefit',
            'MINOR_': 'Some Benefit',
            'RECOVERY_': 'Recovery',
            'MAINTAINING_': 'Maintaining',
            'IMPROVING_': 'Impacting',
            'IMPACTING_': 'Impacting',
            'HIGHLY_': 'Highly Impacting',
            'OVERREACHING_': 'Overreaching'
        }
        for key, value in messages.items():
            if message.startswith(key):
                return value
        return message

    @classmethod
    def from_garmin_json(cls, garmin_response: Dict[str, str]) -> "Activity":
        timecube = Timecube.from_date_time_string(garmin_response.get('startTimeGMT'))
        activity_type, activity_subtype = cls._format_activity_type(
            garmin_response.get('activityType', {}).get('typeKey', 'Unknown')
        )

        if garmin_response.get('averageSpeed'):
            activity_pace = cls._format_pace(garmin_response.get('averageSpeed'))
        else:
            activity_pace = ""

        aerobic_effect = cls._format_training_message(garmin_response.get('aerobicTrainingEffectMessage'))
        anaerobic_effect = cls._format_training_message(garmin_response.get('anaerobicTrainingEffectMessage'))

        icon_url = cls.ACTIVITY_ICONS.get(activity_subtype if activity_subtype != activity_type else activity_type)

        avg_power = None
        max_power = None
        if garmin_response.get('avgPower'):
            avg_power = round(int(garmin_response.get('avgPower')), 1)
        if garmin_response.get('maxPower'):
            max_power = round(int(garmin_response.get('maxPower')), 1)

        distance = 0
        if garmin_response.get('distance'):
            distance = round((int(garmin_response.get('distance'))*0.000621371), 2)

        return cls(
            title=garmin_response.get("activityName"),
            activity_date=timecube,
            type=activity_type,
            subtype=activity_subtype,
            distance=distance,
            duration=round(int(garmin_response.get('duration')), 2),
            cals_burned=round(int(garmin_response.get('calories')), 0),
            avg_pace=activity_pace,
            avg_power=avg_power,
            max_power=max_power,
            training_effect=garmin_response.get('trainingEffectLabel').replace('_', ' ').title(),
            aerobic=round(garmin_response.get('aerobicTrainingEffect', 0), 1),
            aerobic_effect=aerobic_effect,
            anaerobic=round(garmin_response.get('anaerobicTrainingEffect', 0), 1),
            anaerobic_effect=anaerobic_effect,
            pr=bool(garmin_response.get('pr')),
            fav=bool(garmin_response.get('favorite')),
            icon=icon_url
        )
