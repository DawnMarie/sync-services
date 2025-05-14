from data_models.timecube import Timecube

from dataclasses import dataclass, field
from typing import List, Dict, Any
import re


@dataclass
class Event:

    start: Timecube
    end: Timecube
    id: str = ""
    title: str = ""
    calendar: str = ""
    description: str = ""
    duration: int = 0  # duration in minutes
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_gcal_json(cls, gcal_response: Dict[str, Any]) -> "Event":
        start = cls._parse_datetime(gcal_response.get("start", {}))
        end = cls._parse_datetime(gcal_response.get("end", {}))
        description = gcal_response.get("description", "")

        return cls(
            id=gcal_response.get("id", ""),
            title=gcal_response.get("summary", ""),
            calendar=gcal_response.get("organizer", {}).get("displayName", ""),
            description=description,
            start=start,
            end=end,
            duration=int((end.date_in_s - start.date_in_s) / 60) if start and end else 0,
            tags=re.findall(r"#(\w+)", description)
        )

    @staticmethod
    def _parse_datetime(date_obj: Dict[str, str]) -> Timecube | None:
        if date_obj.get("dateTime"):
            return Timecube.from_Y_m_d_H_M_S(date_obj.get("dateTime"))
        else:
            return None

