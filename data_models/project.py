from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from data_models.timecube import Timecube

@dataclass
class Project:

    title: str
    last_updated: Timecube
    am_id: Optional[str] = None # This is _id in AM, AM ID in Notion
    notion_id: Optional[str] = None # This is id in Notion, note in AM
    day: Optional[Timecube] = None
    subcategory: Optional[str] = None  # This is a Subcategory in AM, Value Goal in Notion
    pillar: str = "Inbox" # This is a Category in AM, Pillar in Notion
    goal: Optional[List[str]] = None  # This is a Goal in AM, Goal Outcome in Notion
    depends_on: Optional[List[str]] = None  # Task titles
    planned_week: Optional[str] = None  # In AM, this is the Monday date YYYY-MM-DD; in Notion this is the page title of the related Week, "Week ##"
    planned_month: Optional[str] = None  #In AM, this is YYYY-MM; in Notion this is the page title of the related Month, "Month 2025"
    planned_quarter: Optional[str] = None  # In AM, this is a label combination; in Notion, this is the page title of the related Quarter, "1Q 2025"
    done: bool = False

    @classmethod
    def from_am_json(cls, am_response: Dict[str, str]) -> "Project":
        day = None
        if am_response.get("day"):
            day = Timecube.from_Y_m_d_H_M_S(am_response.get("day"))

        planned_week = None
        if am_response.get("plannedWeek"):
             week_timecube = Timecube.from_Y_m_d(am_response.get("plannedWeek"),"America/New_York" )
             planned_week = "Week " + str(int(week_timecube.week_number) + 1)
        planned_month = None
        if am_response.get("plannedMonth"):
             month_timecube = Timecube.from_Y_m_d(am_response.get("plannedMonth")+"-10")
             planned_month = month_timecube.date_M_Y

        last_updated = Timecube.from_datetime(datetime.now())
        if am_response.get("updatedAt"):
            last_updated = Timecube.from_epoch(int(am_response.get('updatedAt')))

        return cls(
            am_id=am_response.get("_id"),
            title=am_response.get("title"),
            day=day,
            planned_week=planned_week,
            planned_month=planned_month,
            done=bool(am_response.get("done", "")),
            last_updated=last_updated
        )

    @classmethod
    def from_notion_json(cls, notion_response: dict) -> "Project":
        project_properties = notion_response["properties"]

        am_id = None
        if project_properties.get("AM ID").get("rich_text")[0].get("plain_text"):
            am_id = project_properties.get("AM ID").get("rich_text")[0].get("plain_text")

        day = None
        if project_properties.get("Review Date").get("date"):
            day = Timecube.from_Y_m_d(project_properties.get("Review Date").get("date").get("start"), "America/New_York")

        done = False
        if project_properties.get("Status").get("status").get("name") == "Done":
            done = True

        return cls(
            am_id=am_id,  # This is _id in AM, AM ID in Notion
            notion_id=notion_response["id"],
            title=project_properties.get("Project Name").get("title")[0].get("plain_text"),
            day=day,
            last_updated=Timecube.from_date_time_string(notion_response.get("last_edited_time")),
            done=done
        )
