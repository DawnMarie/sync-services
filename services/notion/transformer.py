from data_models.task import Task
from services.notion.database_specific import NotionDatabaseSpecific

from urllib.parse import unquote

class NotionTransformer(NotionDatabaseSpecific):

    @staticmethod
    def _extract_title_from_url(notion_url: str) -> str:
        # Decode URL-encoded characters
        decoded_url = unquote(notion_url)
        # Get the part between the last slash and the ID
        title_with_id = decoded_url.split('/')[-1]
        # Remove the ID portion (32 chars and hyphen)
        title = title_with_id[:-33]
        # Replace remaining hyphens with spaces
        return title.replace('-', ' ')

    def _add_depends_on_title_to_response(self, dependent_on_json: dict):
        for item in dependent_on_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return dependent_on_json

    def _add_project_title_to_response(self, project_json: dict):
        for item in project_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return project_json

    def _add_goal_title_to_response(self, goal_json: dict):
        for item in goal_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return goal_json

    def _add_value_goal_title_to_response(self, value_goal_json: dict):
        for item in value_goal_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return value_goal_json

    def _add_pillar_title_to_response(self, pillar_json: dict):
        for item in pillar_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return pillar_json

    def _add_planned_week_title_to_response(self, planned_week_json: dict):
        for item in planned_week_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return planned_week_json

    def _add_planned_month_title_to_response(self, planned_month_json: dict):
        for item in planned_month_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return planned_month_json

    def _add_planned_quarter_title_to_response(self, planned_quarter_json: dict):
        for item in planned_quarter_json["relation"]:
            item_page = self._get_page_by_id(item["id"])
            item["title"] = self._extract_title_from_url(item_page["url"])
        return planned_quarter_json

    @staticmethod
    def _convert_mood_int_to_str(mood_int: int):
        mood_str = ""
        if mood_int == 9:
            mood_str = "🤩Great"
        if (mood_int == 7) | (mood_int == 8):
            mood_str = "😀Good"
        if mood_int in (6, 5, 4):
            mood_str = "😐Neutral"
        if (mood_int == 3) | (mood_int == 2):
            mood_str = "☹️Bad"
        if mood_int == 1:
            mood_str = "😫Awful"
        return mood_str

    def _convert_task_response_to_dto(self, task_response: dict):
        if task_response["properties"]["Dependent On"]["relation"]:
            task_response["properties"]["Dependent On"] = self._add_depends_on_title_to_response(task_response["properties"]["Dependent On"])

        if task_response["properties"]["Projects"]["relation"]:
            task_response["properties"]["Projects"] = self._add_project_title_to_response(task_response["properties"]["Projects"])

        if task_response["properties"]["Goal Outcome"]["relation"]:
            task_response["properties"]["Goal Outcome"] = self._add_goal_title_to_response(task_response["properties"]["Goal Outcome"])

        if task_response["properties"]["Value Goals"]["relation"]:
            task_response["properties"]["Value Goals"] = self._add_value_goal_title_to_response(task_response["properties"]["Value Goals"])

        if task_response["properties"]["Pillar"]["relation"]:
            task_response["properties"]["Pillar"] = self._add_pillar_title_to_response(task_response["properties"]["Pillar"])

        if task_response["properties"]["Planned Week"]["relation"]:
            task_response["properties"]["Planned Week"] = self._add_planned_week_title_to_response(task_response["properties"]["Planned Week"])

        if task_response["properties"]["Planned Month"]["relation"]:
            task_response["properties"]["Planned Month"] = self._add_planned_month_title_to_response(task_response["properties"]["Planned Month"])

        if task_response["properties"]["Planned Quarter"]["relation"]:
            task_response["properties"]["Planned Quarter"] = self._add_planned_quarter_title_to_response(task_response["properties"]["Planned Quarter"])

        if task_response["properties"]["Sub-item"]["relation"]:
            for i, item in enumerate(task_response["properties"]["Sub-item"]["relation"]):
                subtask = self._get_page_by_id(item["id"])
                item.update({
                    "name": subtask["properties"]["Task"]["title"][0]["plain_text"],
                    "done": subtask["properties"]["Done"]["checkbox"],
                    "time_estimate": subtask["properties"]["Estimated Duration (min)"]["number"]
                })

        return Task.from_notion_json(task_response)

