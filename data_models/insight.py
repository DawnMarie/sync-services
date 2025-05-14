from dataclasses import dataclass


@dataclass
class Insight:

    insight_type: str
    insight: str
    detail: str

    @classmethod
    def from_exist_json(cls, exist_response: dict) -> "Insight":

        insight_type = "Weekly"
        if exist_response["target_date"]:
            insight_type = "Daily"

        insight = exist_response["text"].split("\r\n")

        return cls(
            insight_type=insight_type,
            insight=insight[0],
            detail=insight[1]
        )
