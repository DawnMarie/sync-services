from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import re

from data_models.timecube import Timecube
from data_models.subtask import Subtask

@dataclass
class Task:
    """Represents a task with properties from both Amazing Marvin (AM) and Notion."""

    title: str
    last_updated: Timecube
    am_id: Optional[str] = None # This is _id in AM, AM ID in Notion
    notion_id: Optional[str] = None # This is id in Notion, note in AM
    day: Optional[Timecube] = None
    depends_on: Optional[List[str]] = None  # Task titles
    project: Optional[str] = None  # Project Name
    subcategory: Optional[str] = None  # This is a Subcategory in AM, Value Goal in Notion
    pillar: str = "Inbox" # This is a Category in AM, Pillar in Notion
    goal: Optional[List[str]] = None  # This is a Goal in AM, Goal Outcome in Notion
    time_estimate: Optional[int] = None  # In minutes; timeEstimate (ms) in AM, Estimated Duration in Notion
    duration: Optional[int] = None  # In minutes; duration (ms) in AM, Tracked Time in Notion
    planned_week: Optional[str] = None  # In AM, this is the Monday date YYYY-MM-DD; in Notion this is the page title of the related Week, "Week ##"
    planned_month: Optional[str] = None  #In AM, this is YYYY-MM; in Notion this is the page title of the related Month, "Month 2025"
    planned_quarter: Optional[str] = None  # In AM, this is a label combination; in Notion, this is the page title of the related Quarter, "1Q 2025"
    subtasks: Optional[List[Subtask]] = None  #In AM, this is a clear Task -> Subtask relationship. In Notion, this is a Parent item -> Sub-item relationship
    tags: Optional[List[str]] = None
    done: bool = False

    @staticmethod
    def _convert_ms_to_minutes(milliseconds: Optional[int]) -> Optional[int]:
        """Convert milliseconds to minutes."""
        if milliseconds:
            return int(int(milliseconds) / Subtask.MILLISECONDS_TO_MINUTES)
        return None

    @staticmethod
    def count_incomplete_done(task_list: List["Task"]) -> dict:
        """Count completed and incomplete tasks in a list."""
        task_counts = {'done': 0, 'incomplete': 0}
        for task in task_list:
            if task.done is True:
                task_counts['done'] = int(task_counts['done']) + 1
            else:
                task_counts['incomplete'] = int(task_counts['incomplete']) + 1
        return task_counts

    @staticmethod
    def _parse_time_and_text(task_title: str, base_date: Timecube) -> tuple[Timecube, str]:
        """
        Extracts time from string like "5:30 pm Scheduled Task", adds it to base_date,
        and returns tuple of (new_datetime, actual_task_title)
        """
        # Regular expression to match time in format "H:MM am/pm"
        time_pattern = r'^(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)'

        match = re.match(time_pattern, task_title)
        if not match:
            return base_date, task_title

        hours, minutes, meridiem = match.groups()
        hours = int(hours)
        minutes = int(minutes)

        # Convert to 24-hour format if PM
        if meridiem.lower() == 'pm' and hours != 12:
            hours += 12
        elif meridiem.lower() == 'am' and hours == 12:
            hours = 0

        # Create new Timecube with original date but new time
        updated_base_date = base_date.date_in_datetime.replace(
            hour=hours,
            minute=minutes,
            second=0,
            microsecond=0
        )
        new_timecube = Timecube.from_datetime(updated_base_date)
        new_timecube.local_tz = "America/New_York"

        # Get the remaining text (strip to remove extra spaces)
        actual_task_title = task_title[match.end():].strip()

        return new_timecube, actual_task_title

    @classmethod
    def from_am_json(cls, am_response: Dict[str, str]) -> "Task":
        """Create a Task instance from Amazing Marvin JSON response."""
        title = am_response.get("title")
        day = None

        if ("day" in am_response) & (am_response.get("day") != "unassigned"):
            day = Timecube.from_Y_m_d(am_response.get("day"), "America/New_York")
        day, title = cls._parse_time_and_text(title, day)

        time_estimate = cls._convert_ms_to_minutes(am_response.get("timeEstimate"))
        duration = cls._convert_ms_to_minutes(am_response.get("duration"))

        planned_week = None
        if am_response.get("plannedWeek"):
             week_timecube = Timecube.from_Y_m_d(am_response.get("plannedWeek"),"America/New_York" )
             planned_week = "Week " + str(int(week_timecube.week_number))
        planned_month = None
        if am_response.get("plannedMonth"):
             month_timecube = Timecube.from_Y_m_d(am_response.get("plannedMonth")+"-10")
             planned_month = month_timecube.date_M_Y

        last_updated = Timecube.from_datetime(datetime.now())
        if am_response.get("updatedAt"):
            last_updated = Timecube.from_epoch(int(am_response.get('updatedAt')))

        return cls(
            am_id=am_response.get("_id"),
            title=title,
            day=day,
            time_estimate=time_estimate,
            duration=duration,
            planned_week=planned_week,
            planned_month=planned_month,
            last_updated=last_updated,
            done=bool(am_response.get("done", "")),
        )

    @classmethod
    def from_notion_json(cls, notion_response: dict) -> "Task":
        """Create a Task instance from Notion JSON response."""
        task_properties = notion_response["properties"]

        am_id = None
        if task_properties.get("AM ID").get("rich_text")[0].get("plain_text"):
            am_id = task_properties.get("AM ID").get("rich_text")[0].get("plain_text")

        day = None
        if task_properties.get("Scheduled").get("date"):
            day = Timecube.from_date_time_string(task_properties.get("Scheduled").get("date").get("start"), "America/New_York")

        depends_on = []
        if task_properties.get("Dependent On").get("relation"):
            for item in task_properties.get("Depends On").get("relation"):
                depends_on.append(item.get("title"))

        project = None
        if task_properties.get("Projects").get("relation"):
            for item in task_properties.get("Projects").get("relation"):
                project = item.get("title")

        subcategory = None
        if task_properties.get("Value Goals").get("relation"):
            for item in task_properties.get("Value Goals").get("relation"):
                subcategory = item.get("title")

        pillar = None
        if task_properties.get("Pillar").get("relation"):
            for item in task_properties.get("Pillar").get("relation"):
                pillar = item.get("title")

        goal = None
        if task_properties.get("Goal Outcome").get("relation"):
                for item in task_properties.get("Goal Outcome").get("relation"):
                    goal = item.get("title")

        planned_week = None
        if task_properties.get("Planned Week").get("relation"):
            for item in task_properties.get("Planned Week").get("relation"):
                planned_week = item.get("title")

        planned_month = None
        if task_properties.get("Planned Month").get("relation"):
            for item in task_properties.get("Planned Month").get("relation"):
                planned_month = item.get("title")

        planned_quarter = None
        if task_properties.get("Planned Quarter").get("relation"):
            for item in task_properties.get("Planned Quarter").get("relation"):
                planned_quarter = item.get("title")

        time_estimate = None
        if task_properties.get("Estimated Duration (min)").get("number"):
            time_estimate = task_properties.get("Estimated Duration (min)").get("number")

        duration = None
        if task_properties.get("Tracked Time (min)").get("number"):
            duration = task_properties.get("Tracked Time (min)").get("number")

        return cls(
            am_id=am_id,
            notion_id=notion_response["id"],
            day=day,
            depends_on=depends_on,
            project=project,
            subcategory=subcategory,
            pillar=pillar,
            goal=goal,
            title=task_properties.get("Task").get("title")[0].get("plain_text"),
            time_estimate=time_estimate,
            duration=duration,
            planned_week=planned_week,
            planned_month=planned_month,
            planned_quarter=planned_quarter,
            done=bool(task_properties["Done"]["checkbox"]),
            last_updated=Timecube.from_date_time_string(notion_response.get("last_edited_time"))
        )
