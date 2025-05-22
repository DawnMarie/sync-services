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
    duration: float = 0  # in minutes
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

    ACTIVITY_COMPARISON_FIELDS = [
        'title', 'type', 'subtype', 'distance', 'duration', 'cals_burned',
        'avg_pace', 'training_effect', 'aerobic', 'aerobic_effect',
        'anaerobic', 'anaerobic_effect', 'pr', 'fav', 'icon'
    ]

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
            duration=round(int(garmin_response.get('duration'))/60, 2),
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

    @classmethod
    def from_notion_json(cls, notion_response: dict) -> "Activity":
        """Create an Activity instance from Notion JSON response."""
        activity_properties = notion_response["properties"]

        # Extract activity date
        activity_date = Timecube.from_date_time_string(activity_properties.get("Date").get("date").get("start"))

        # Extract activity type and subtype
        activity_type = activity_properties.get("Activity Type").get("select").get("name")
        activity_subtype = activity_properties.get("Subactivity Type").get("select").get("name")

        # Extract title
        title = activity_properties.get("Activity Name").get("title")[0].get("plain_text")

        # Extract numeric values
        distance = activity_properties.get("Distance (miles)").get("number") or 0
        duration = activity_properties.get("Duration (min)").get("number") or 0
        cals_burned = activity_properties.get("Calories").get("number") or 0

        # Extract pace
        avg_pace = ""
        if activity_properties.get("Avg Pace").get("rich_text"):
            avg_pace = activity_properties.get("Avg Pace").get("rich_text")[0].get("plain_text")

        # Extract power values
        avg_power = activity_properties.get("Avg Power").get("number")
        max_power = activity_properties.get("Max Power").get("number")

        # Extract training effect
        training_effect = activity_properties.get("Training Effect").get("select").get("name")

        # Extract aerobic and anaerobic values
        aerobic = activity_properties.get("Aerobic").get("number") or 0
        aerobic_effect = activity_properties.get("Aerobic Effect").get("select").get("name")
        anaerobic = activity_properties.get("Anaerobic").get("number") or 0
        anaerobic_effect = activity_properties.get("Anaerobic Effect").get("select").get("name")

        # Extract boolean values
        pr = activity_properties.get("PR").get("checkbox")
        fav = activity_properties.get("Fav").get("checkbox")

        # Get icon URL based on activity type/subtype
        icon_url = cls.ACTIVITY_ICONS.get(activity_subtype if activity_subtype != activity_type else activity_type)

        return cls(
            title=title,
            activity_date=activity_date,
            type=activity_type,
            subtype=activity_subtype,
            distance=distance,
            duration=duration,
            cals_burned=cals_burned,
            avg_pace=avg_pace,
            avg_power=avg_power,
            max_power=max_power,
            training_effect=training_effect,
            aerobic=aerobic,
            aerobic_effect=aerobic_effect,
            anaerobic=anaerobic,
            anaerobic_effect=anaerobic_effect,
            pr=pr,
            fav=fav,
            icon=icon_url
        )

    def is_different_than(self, other_activity: "Activity") -> bool:
        """
        Compare this activity with another activity and determine if they have any differences in their fields.

        Args:
            other_activity: Another Activity object to compare with

        Returns:
            bool: True if activities have differences, False if they are identical
        """
        def _compare_field(field_name: str) -> bool:
            return getattr(self, field_name) != getattr(other_activity, field_name)

        return any(_compare_field(field) for field in self.ACTIVITY_COMPARISON_FIELDS)
