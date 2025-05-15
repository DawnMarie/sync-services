from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Subtask:
    """Represents a subtask with its properties and conversion methods."""

    # Constants
    MILLISECONDS_TO_MINUTES = 60000

    # Fields with improved type hints and defaults
    am_id: Optional[str] = None  # Unique ID, same as the key in the parent task's subtasks dict
    notion_id: Optional[str] = None
    title: str = ""
    done: bool = False
    time_estimate: Optional[int] = None  # in minutes

    @staticmethod
    def _convert_ms_to_minutes(milliseconds: Optional[int]) -> Optional[int]:
        """Convert milliseconds to minutes."""
        if milliseconds:
            return int(int(milliseconds) / Subtask.MILLISECONDS_TO_MINUTES)
        return None

    @classmethod
    def from_am_json(cls, am_response: Dict[str, str]) -> "Subtask":
        """
        Create a Subtask instance from Amazing Marvin JSON response.

        Args:
            am_response: Dictionary containing Amazing Marvin response data

        Returns:
            Subtask: New instance with populated fields
        """
        time_estimate = cls._convert_ms_to_minutes(am_response.get("timeEstimate"))

        return cls(
            am_id=am_response.get("_id"),
            title=am_response.get("title"),
            done=bool(am_response.get("done", False)),
            time_estimate=time_estimate
        )

    @classmethod
    def from_notion_json(cls, notion_response: dict) -> "Subtask":
        """
        Create a Subtask instance from Notion JSON response.

        Args:
            notion_response: Dictionary containing Notion response data

        Returns:
            Subtask: New instance with populated fields
        """
        return cls(
            am_id=notion_response.get("properties").get("AM ID").get("rich_text")[0].get("plain_text"),
            notion_id=notion_response.get("id"),
            title=notion_response.get("properties").get("Task").get("title")[0].get("plain_text"),
            done=notion_response.get("properties").get("Done").get("checkbox"),
            time_estimate=notion_response.get("properties").get("Estimated Duration (min)").get("number")
        )
