from data_models.activity import Activity
from data_models.insight import Insight
from data_models.personal_record import PR
from data_models.project import Project
from data_models.sleep import Sleep
from data_models.subtask import Subtask
from data_models.task import Task
from data_models.timecube import Timecube

from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from notion_client import Client
from typing import List
import os
import pytz


class NotionService:
    load_dotenv()

    def __init__(self):
        notion_token = os.getenv("NOTION_TOKEN")
        self.client = Client(auth=notion_token)

        self.activity_database_id = os.getenv("NOTION_ACTIVITY_DB_ID")
        self.pr_database_id = os.getenv("NOTION_PR_DB_ID")
        self.sleep_database_id = os.getenv("NOTION_SLEEP_DB_ID")
        self.stats_database_id = os.getenv("NOTION_STATS_DB_ID")
        self.steps_database_id = os.getenv("NOTION_STEPS_DB_ID")

        self.daily_tracking_database_id = os.getenv("NOTION_DAILY_TRACKING_DB_ID")

        self.pillar_database_id = os.getenv("NOTION_PILLAR_DB_ID")
        self.project_database_id = os.getenv("NOTION_PROJECT_DB_ID")
        self.week_database_id = os.getenv("NOTION_WEEK_DB_ID")
        self.month_database_id = os.getenv("NOTION_MONTH_DB_ID")
        self.quarter_database_id = os.getenv("NOTION_QUARTER_DB_ID")
        self.tasks_database_id = os.getenv("NOTION_TASKS_DB_ID")

        self.stepbet_database_id = os.getenv("NOTION_STEPBET_DB_ID")

        self.habit_database_id = os.getenv("NOTION_HABIT_DB_ID")
        self.mood_database_id = os.getenv("NOTION_MOOD_DB_ID")

        self.insight_block_id = os.getenv("NOTION_INSIGHT_BLOCK_ID")

    """
    Generic GET/POST functions
    """

    def _get_database_page_by_field(self, database_id: str, field_name: str, field_value: str) -> str:
        page = "No page returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "rich_text": {"contains": field_value}
                }]
            }
        )
        if query['results'][0]:
            page = query['results'][0]
        return page

    def _get_database_page_id_by_name(self, database_id: str, field_name: str, page_name: str) -> str:
        page_id = "No page id returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "title": {"equals": page_name}
                }]
            }
        )
        if query['results'][0]['id']:
            page_id = query['results'][0]['id']
        return page_id

    def _get_database_page_id_by_date(self, database_id: str, field_name: str, search_date: Timecube) -> str:
        page_id = "No page id returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "date": {"equals": search_date.date_Y_m_d}
                }]
            }
        )
        if query['results'][0]['id']:
            page_id = query['results'][0]['id']
        return page_id

    def _get_page_by_id(self, page_id: str) -> dict:
        page = "No page returned!"
        query = self.client.pages.retrieve(page_id=page_id)
        if query:
            page = query
        return page

    def _get_page_name_by_id(self, page_id: str, title_field: str):
        page_name = "No page returned!"
        query = self.client.pages.retrieve(page_id=page_id)
        if query:
            page_name = query['properties'][title_field]['title'][0]['plain_text']
        return page_name

    def _get_database_pages_by_last_edited(self, database_id: str, minutes_in_the_past: int) -> List[dict]:
        search_datetime = datetime.now() - timedelta(minutes=minutes_in_the_past)
        tasks = []
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "timestamp": "last_edited_time",
                    "last_edited_time": {
                    "on_or_after": search_datetime.isoformat(timespec='seconds')
                },
            }
        )
        if query['results']:
            tasks = query['results']
        return tasks

    def _get_block_children_by_id(self, block_id: str) -> List[str]:
        block_ids = []
        query = self.client.blocks.children.list(
            block_id=block_id
        )
        for item in query["results"]:
            block_ids.append(item["id"])
        return block_ids

    def _update_block_text(self, text: str, block_id: str, block_type: str):
        properties = {
            "rich_text": [{
                "text": {"content": text},
                "plain_text": text
            }]
        }
        update = {
            "block_id": block_id,
            block_type: properties
        }
        return self.client.blocks.update(**update)

    def _update_database_page(self, page_id: str, fields: dict):
        update = {
            "page_id": page_id,
            "properties": fields
        }
        return self.client.pages.update(**update)

    """
    GET/POST/PATCH methods for specific databases or blocks or pages
    """
    def _get_pillar_page_id_by_name(self, pillar: str) -> str:
        return self._get_database_page_id_by_name(self.pillar_database_id, "Pillar", pillar)

    def _get_project_page_id_by_name(self, project: str) -> str:
        return self._get_database_page_id_by_name(self.project_database_id, "Project Name", project)

    def _get_habits_from_daily_page_by_date(self, date: Timecube) -> List[str]:
        days_page = self._get_database_page_id_by_date(self.daily_tracking_database_id, "Date", date)
        all_page_properties = self._get_page_by_id(days_page)
        #logic to get the habits that have been checked
        return all_page_properties["properties"]["Habits"]["relation"]

    def _get_week_page_id_by_name(self, week: str) -> str:
        return self._get_database_page_id_by_name(self.week_database_id, "Name", week)

    def _get_month_page_id_by_name(self, month: str) -> str:
        return self._get_database_page_id_by_name(self.month_database_id, "Name", month)

    def _get_quarter_page_id_by_name(self, quarter: str) -> str:
        return self._get_database_page_id_by_name(self.quarter_database_id, "Quarter", quarter)

    def _get_task_page_id_by_name(self, task: str) -> str:
        return self._get_database_page_id_by_name(self.tasks_database_id, "Title", task)

    def _get_task_page_by_am_id(self, am_id: str):
        return self._get_database_page_by_field(self.tasks_database_id, "AM ID", am_id)

    def _get_task_page_name_by_id(self, task_id: str) -> str:
        return self._get_page_name_by_id(task_id, "Task")

    def _get_week_page_by_id(self, week_id: str) -> str:
        return self._get_page_name_by_id(week_id, "Name")

    def _get_month_page_by_id(self, month_id: str) -> str:
        return self._get_page_name_by_id(month_id, "Name")

    def _get_goal_outcome_page_name_by_id(self, goal_id: str) -> str:
        return self._get_page_name_by_id(goal_id, "Name")

    def _get_daily_tracking_page_id_by_name(self, todays_page: str) -> str:
        return self._get_database_page_id_by_name(self.daily_tracking_database_id, "Today's Page", todays_page)

    def _get_pr_page_id_by_name(self, pr: str) -> str:
        return self._get_database_page_id_by_name(self.pr_database_id, "Record", pr)

    def _get_fitness_stats_page_by_date(self, page_date: Timecube):
        return self._get_database_page_id_by_date(self.stats_database_id, "Today's Date", page_date)

    def _get_steps_page_id_by_name(self, page_title: str) -> str:
        return self._get_database_page_id_by_name(self.steps_database_id, "Activity", page_title)

    def _get_task_pages_by_last_edited(self, minutes_in_the_past: int) -> List[dict]:
        return self._get_database_pages_by_last_edited(self.tasks_database_id, minutes_in_the_past)

    def _get_current_stepbet_games(self):
        """
        Pull the page ids of the current StepBet games so that the step goal
        can be pulled into the Garmin Daily Steps database
        :return:
        """
        page_ids = []
        query = self.client.databases.query(
            database_id=self.stepbet_database_id,
            filter={
                "and": [
                    {"property": "Start Date", "date": {"on_or_before": date.today().isoformat()}},
                    {"property": "End Date", "date": {"on_or_after": date.today().isoformat()}}
                ]
            }
        )
        for item in query['results']:
            page_ids.append(item['id'])
        return page_ids

    def _post_new_task(self, task: Task) -> str:
        project_id = self._get_project_page_id_by_name(task.project)

        properties = {
            "Task": {
                "id": "title",
                "title": [{"text": {"content": task.title}}]
            },
            "Projects (DB)": {
                "relation": [{"id": project_id}]
            },
            "Tracked Time (min)": {
                "number": task.duration
            },
            "Estimated Duration (min)": {
                "number": task.time_estimate
            },
            "AM ID": {
                "rich_text": [{"text": {"content": task.am_id}}]
            }
        }

        if task.done:
            status = "Done"
            properties["Done"] = {
                "checkbox": True
            }
        else:
            status = "Active"
        properties["Done"] = {
            "checkbox": False
        }
        properties["Status"] = {"status": {"name": status}}

        if task.day:
            properties["Scheduled"] = {
                "date": {"start": task.day.date_time_Y_m_d_H_M_S}
            }

        if task.planned_week:
            week_id = self._get_week_page_id_by_name(task.planned_week)
            properties["Planned Week"] = {
                "relation": [{"id": week_id}]
            }

        if task.planned_month:
            month_id = self._get_month_page_id_by_name(task.planned_month)
            properties["Planned Month"] = {
                "relation": [{"id": month_id}]
            }

        page = {
            "parent": {"database_id": self.tasks_database_id},
            "properties": properties,
        }
        return self.client.pages.create(**page)["id"]

    def _post_new_subtask(self, subtask: Subtask) -> str:
        if subtask.done:
            status = "Done"
        else:
            status = "Active"
        properties = {
            "Task": {
                "title": [{"text": {"content": subtask.title}}]
            },
            "Status": {
                "status": {"name": status}
            },
            "Estimated Duration (min)": {
                "number": subtask.time_estimate
            }
        }
        page = {
            "parent": {"database_id": self.tasks_database_id},
            "properties": properties,
        }
        return self.client.pages.create(**page)["id"]

    def _post_daily_insight(self, insight: Insight, insight_id: str, detail_id: str):
        return self._update_block_text(insight.insight, insight_id, "heading_2"), self._update_block_text(insight.detail, detail_id, "heading_3")

    def _post_weekly_insight(self, insight: Insight, insight_id: str, detail_id: str):
        return self._update_block_text(insight.insight, insight_id, "heading_3"), self._update_block_text(insight.detail, detail_id, "text")

    def _post_today_mood(self, mood_str: str):
        today = datetime.now(pytz.timezone("America/New_York")).date().isoformat()
        page_title = f"Mood {datetime.today().strftime('%Y.%m.%d')}"
        properties = {
            "Mood": {"select": {"name": mood_str}},
            "Date": {"date": {"start": today}},
            "Name": {"title": [{"text": {"content": page_title}}]}
        }
        page = {
            "parent": {"database_id": self.mood_database_id},
            "properties": properties
        }
        return self.client.pages.create(**page)

    def _post_training_page(
            self, timecube: Timecube, daily_average_stress: int,
            training_readiness: int, readiness_description: str, training_status: str):
        properties = {
            "Today's Date": {
                "date": {"start": timecube.date_Y_m_d}
            },
            "Average Stress": {
                "number": daily_average_stress
            },
            "Readiness Score": {
                "number": training_readiness
            },
            "Readiness Description": {
                "rich_text": [{"text": {"content": readiness_description}}]
            },
            "Training Status": {
                "title": [{"text": {"content": training_status}}]
            }
        }
        page = {
            "parent": {"database_id": self.stats_database_id},
            "properties": properties
        }
        return self.client.pages.create(**page)

    def _update_fitness_stats_page(
            self, training_status: str, training_readiness: int, readiness_description: str, daily_average_stress: int):
        todays_date = Timecube.from_datetime(datetime.today())
        page_id = self._get_fitness_stats_page_by_date(todays_date)
        properties = {
            "Training Status": {"title": [{"text": {"content": training_status}}]},
            "Readiness Score": {"number": training_readiness},
            "Readiness Description": {"rich_text": [{"text": {"content": readiness_description}}]},
            "Average Stress": {"number": daily_average_stress}
        }
        return self._update_database_page(page_id, properties)

    def _update_daily_tracking_page(self, field: str, field_type: str, value: str | int):
        todays_page = f"Daily Log - {datetime.today().strftime('%Y.%m.%d')}"
        page_id = self._get_daily_tracking_page_id_by_name(todays_page)
        properties = {
            field: {field_type: value}
        }
        return self._update_database_page(page_id, properties)

    def _update_steps_page(self, steps: int, total_distance: int):
        today = Timecube.from_datetime(datetime.today())
        todays_page = "Walking " + today.date_Y_m_d
        page_id = self._get_steps_page_id_by_name(todays_page)
        properties = {
            "Total Steps": {
                "number": steps
            },
            "Total Distance (miles)": {
                "number": total_distance
            }
        }
        return self._update_database_page(page_id, properties)

    """
    Utility functions to modify or edit data, not specifically to create or update objects in Notion
    """
    def _add_subtask_to_task(self, subtask: Subtask, parent_id: str):
        subtask_id = self._post_new_subtask(subtask)
        properties = {
            "Sub-item": {
                "relation": [{"id": subtask_id}]
            }
        }
        update = {
            "page_id": parent_id,
            "properties": properties
        }
        return self.client.pages.update(**update)["id"]

    def _add_dependency_to_task(self, task_id: str, dependency: str):
        dependency_id = self._get_task_page_id_by_name(dependency)
        properties = {
            "Dependent On": {
                "relation": [{"id": dependency_id}]
            }
        }
        update = {
            "page_id": task_id,
            "properties": properties
        }
        return self.client.pages.update(**update)["id"]

    @staticmethod
    def _format_hours_to_hm(hours: float) -> str:
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

    def _add_depends_on_title_to_response(self, notion_response):
        for item in notion_response["relation"]:
            item["title"] = self._get_task_page_name_by_id(item["id"])
        return notion_response

    def _add_goal_title_to_response(self, notion_response):
        for item in notion_response["relation"]:
            item["title"] = self._get_goal_outcome_page_name_by_id(item["id"])
        return notion_response

    def _convert_task_response_to_dto(self, task_response: dict):
        if task_response["properties"]["Dependent On"]["relation"]:
            self._add_depends_on_title_to_response(task_response["properties"]["Dependent On"])

        if task_response["properties"]["Goal Outcome (DB)"]["relation"]:
            self._add_goal_title_to_response(task_response["properties"]["Goal Outcome (DB)"])

        if task_response["properties"]["Sub-item"]["relation"]:
            for i, item in enumerate(task_response["properties"]["Sub-item"]["relation"]):
                subtask = self._get_page_by_id(item["id"])
                item.update({
                    "name": subtask["properties"]["Task"]["title"][0]["plain_text"],
                    "done": subtask["properties"]["Done"]["checkbox"],
                    "time_estimate": subtask["properties"]["Estimated Duration (min)"]["number"]
                })

        if task_response["properties"]["Planned Week"]["relation"]:
            task_response["properties"]["Planned Week"]["relation"][0]["week"] = (
                self._get_week_page_by_id(task_response["properties"]["Planned Week"]["relation"][0]["id"]))

        if task_response["properties"]["Planned Month"]["relation"]:
            task_response["properties"]["Planned Month"]["relation"][0]["month"] = (
                self._get_month_page_by_id(task_response["properties"]["Planned Month"]["relation"][0]["id"]))

        return Task.from_notion_json(task_response)

    """
    Public functions
    """
    def get_tasks_by_last_edited(self, minutes_in_the_past: int) -> List[Task]:
        tasks = []
        tasks_response = self._get_task_pages_by_last_edited(minutes_in_the_past)
        for task in tasks_response:
            task_dto = self._convert_task_response_to_dto(task)
            tasks.append(task_dto)
        return tasks

    def get_task_by_am_id(self, am_id: str) -> Task:
        task_response = self._get_task_page_by_am_id(am_id)
        task_dto = self._convert_task_response_to_dto(task_response)
        return task_dto

    def post_new_project(self, project: Project):
        pillar_id = self._get_pillar_page_id_by_name(project.pillar)
        properties = {
            "Project Name": {
                "title": [{"text": {"content": project.title}}]
            },
            "Pillars (DB)": {
                "relation": [{"id": pillar_id}]
            },
            "Status": {
                "status": {
                    "name": "In progress"
                }
            }
        }

        if project.planned_quarter:
            quarter_id = self._get_quarter_page_id_by_name(project.planned_quarter)
            properties["Quarter (DB)"] = {
                "relation": [{"id": quarter_id}]
            }

        if project.day:
            properties["Review Date"] = {
                "date": {"start": project.day.date_time_Y_m_d_H_M_S}
            }

        page = {
            "parent": {"database_id": self.project_database_id},
            "properties": properties,
        }
        return self.client.pages.create(**page)

    def post_task_with_subtasks(self, task: Task) -> str:
        task_id = self._post_new_task(task)
        if task.subtasks:
            for subtask in task.subtasks:
                task_id = self._add_subtask_to_task(subtask, task_id)
        return task_id

    def update_task_dependencies(self, task: Task) -> str:
        task_id = ""
        for dependency in task.depends_on:
            task_id = self._add_dependency_to_task(task_id, dependency)
        return task_id

    def post_daily_insights(self, daily_insights: List[Insight]):
        block_ids = self._get_block_children_by_id(self.insight_block_id)
        insight_responses = [self._post_daily_insight(daily_insights[0], block_ids[1], block_ids[2]),
                             self._post_daily_insight(daily_insights[1], block_ids[3], block_ids[4]),
                             self._post_daily_insight(daily_insights[2], block_ids[5], block_ids[6]),
                             self._post_weekly_insight(daily_insights[3], block_ids[8], block_ids[9]),
                             self._post_weekly_insight(daily_insights[4], block_ids[10], block_ids[11]),
                             self._post_weekly_insight(daily_insights[5], block_ids[12], block_ids[13])]
        return insight_responses

    def post_today_training_entries(
            self, training_status: str, training_readiness: int, training_description: str, daily_average_stress: int):
        timecube = Timecube.from_datetime(datetime.today())
        return self._post_training_page(
            timecube, daily_average_stress, training_readiness, training_description, training_status)

    def post_activity_entry(self, activity: Activity):
        properties = {
            "Date": {"date": {"start": activity.activity_date.date_time_Y_m_d_H_M_S}},
            "Activity Type": {"select": {"name": activity.type}},
            "Subactivity Type": {"select": {"name": activity.subtype}},
            "Activity Name": {"title": [{"text": {"content": activity.title}}]},
            "Distance (miles)": {"number": activity.distance},
            "Duration (min)": {"number": activity.duration},
            "Calories": {"number": activity.cals_burned},
            "Avg Pace": {"rich_text": [{"text": {"content": activity.avg_pace}}]},
            "Avg Power": {"number": activity.avg_power},
            "Max Power": {"number": activity.max_power},
            "Training Effect": {"select": {"name": activity.training_effect}},
            "Aerobic": {"number": activity.aerobic},
            "Aerobic Effect": {"select": {"name": activity.aerobic_effect}},
            "Anaerobic": {"number": activity.anaerobic},
            "Anaerobic Effect": {"select": {"name": activity.anaerobic_effect}},
            "PR": {"checkbox": activity.pr},
            "Fav": {"checkbox": activity.fav}
        }
        page = {
            "parent": {"database_id": self.activity_database_id},
            "icon": {"type": "external", "external": {"url": activity.icon}},
            "properties": properties
        }
        return self.client.pages.create(**page)

    def post_sleep_entry(self, sleep: Sleep, skip_zero_sleep=True) -> str:
        """Creates a page in the Sleep Database. Returns the new page id"""
        if skip_zero_sleep and sleep.total_sleep == 0:
            return f"Skipping sleep data for {sleep.start_time.date_Y_m_d} as total sleep is 0"

        properties = {
            "Date": {
                "title": [{"text": {"content": "Sleep " + sleep.start_time.date_for_titles}}]
            },
            "Times": {
                "rich_text": [
                    {"text": {
                        "content": f"{sleep.start_time.clock_time_H_M} → {sleep.end_time.clock_time_H_M}"}}]},
            "Long Date": {"date": {"start": sleep.start_time.date_time_Y_m_d_H_M_S}},
            "Full Date/Time": {"date": {"start": sleep.start_time.date_time_Y_m_d_H_M_S,
                                        "end": sleep.end_time.date_time_Y_m_d_H_M_S}},
            "Total Sleep (h)": {"number": sleep.total_sleep},
            "Light Sleep (h)": {"number": sleep.light_sleep},
            "Deep Sleep (h)": {"number": sleep.deep_sleep},
            "REM Sleep (h)": {"number": sleep.rem_sleep},
            "Awake Time (h)": {"number": sleep.awake_time},
            "Total Sleep": {
                "rich_text": [{"text": {"content": self._format_hours_to_hm(sleep.total_sleep)}}]},
            "Light Sleep": {
                "rich_text": [{"text": {"content": self._format_hours_to_hm(sleep.light_sleep)}}]},
            "Deep Sleep": {
                "rich_text": [{"text": {"content": self._format_hours_to_hm(sleep.deep_sleep)}}]},
            "REM Sleep": {
                "rich_text": [{"text": {"content": self._format_hours_to_hm(sleep.rem_sleep)}}]},
            "Awake Time": {
                "rich_text": [{"text": {"content": self._format_hours_to_hm(sleep.awake_time)}}]},
            "Resting HR": {"number": sleep.resting_hr if hasattr(sleep, 'resting_hr') else 0}
        }

        response = self.client.pages.create(
            parent={"database_id": self.sleep_database_id},
            properties=properties,
            icon={"emoji": "😴"})
        return response['id']

    def post_steps_entry(self, entry_date: Timecube, steps: int, total_distance: int, stepbet_links: List[str]):
        """Add a new page to the Step Database with the day's steps. Returns the id of the created page"""
        links_payload = []
        for item in stepbet_links:
            links_payload.append({'id': item})
        properties_payload = {
            "Activity": {
                "title": [{"text": {"content": "Walking " + entry_date.date_Y_m_d}}]
            },
            "Date": {
                "date": {"start": entry_date.date_Y_m_d}
            },
            "Total Steps": {
                "number": steps
            },
            "Total Distance (miles)": {
                "number": total_distance
            },
            "StepBet Link": {
                "relation": links_payload
            }
        }
        steps_payload = {
            "parent": {"database_id": self.steps_database_id},
            "properties": properties_payload
        }
        response = self.client.pages.create(**steps_payload)
        return response['id']

    def update_mobile_screen_time(self, mobile_screen_time):
        return self._update_daily_tracking_page("Mobile Screen Time (min)", "number", mobile_screen_time)

    def update_daily_note(self, daily_note: str, mood: int):
        daily_note = [{"text": {"content": daily_note}}]
        daily_note_response = self._update_daily_tracking_page("Daily Note", "rich_text", daily_note)
        mood_str = ""
        if mood == 9:
            mood_str = "🤩Great"
        if (mood == 7) | (mood == 8):
            mood_str = "😀Good"
        if mood in (6, 5, 4):
            mood_str = "😐Neutral"
        if (mood == 3) | (mood == 2):
            mood_str = "☹️Bad"
        if mood == 1:
            mood_str = "😫Awful"
        mood = {"name": mood_str}
        daily_mood_response = self._update_daily_tracking_page("Mood", "select", mood)
        mood_tracker_response = self._post_today_mood(mood_str)
        return daily_note_response, daily_mood_response, mood_tracker_response

    def update_calorie_entries(self, calories_in: int, calories_out: int):
        return self._update_daily_tracking_page("Calories In", "number", calories_in), \
            self._update_daily_tracking_page("Calories Out", "number", calories_out)

    def update_menstrual_cycle(self, menstrual_cycle_day: int):
        return self._update_daily_tracking_page("Cycle Day", "number", menstrual_cycle_day)

    def update_training_entries(
            self, training_status: str, training_readiness: int, readiness_description: str, daily_average_stress: int):
        # update Daily Tracking Page
        status_properties = [{"text": {"content": training_status}}]
        readiness_properties = [{"text": {"content": readiness_description}}]
        status_daily_response = self._update_daily_tracking_page("Training Status", "rich_text", status_properties)
        readiness_daily_response = self._update_daily_tracking_page("Readiness Score", "number", training_readiness)
        description_daily_response = \
            self._update_daily_tracking_page("Readiness Description", "rich_text", readiness_properties)
        stress_daily_response = self._update_daily_tracking_page("Average Stress", "number", daily_average_stress)

        # update Stats Page for day
        stats_response = self._update_fitness_stats_page(
            training_status, training_readiness, readiness_description, daily_average_stress)

        return status_daily_response, readiness_daily_response, \
            description_daily_response, stress_daily_response, stats_response

    def update_weight_bodyfat(self, weight: int, body_fat: int):
        weight_daily_response = self._update_daily_tracking_page("Weight", "number", weight)
        bf_daily_response = self._update_daily_tracking_page("Body Fat", "number", body_fat)
        return weight_daily_response, bf_daily_response

    def update_pr_entry(self, record: PR):
        page_id = self._get_pr_page_id_by_name(record.activity_name)
        properties = {
            "Date": {"date": {"start": record.activity_date.date_time_Y_m_d_H_M_S}},
            "PR": {"checkbox": True}
        }

        if record.value:
            properties["Value"] = {"rich_text": [{"text": {"content": record.value}}]}
        if record.pace:
            properties["Pace"] = {"rich_text": [{"text": {"content": record.pace}}]}

        return self.client.pages.update(
            page_id=page_id,
            properties=properties,
            icon={"emoji": record.icon}
        )

    def update_steps_entries(self, steps: int, total_distance: int):
        """
        Update existing step counts
        """
        # Daily Tracking DB
        dt_steps_response = self._update_daily_tracking_page("Steps", "number", steps)

        # Garmin Steps DB
        steps_response = self._update_steps_page(steps, total_distance)
        return dt_steps_response, steps_response

    def update_task(self, task: Task) -> None:
        """
        Update a task in Notion.
        """
        try:
            # Create a dictionary of fields to update
            fields = {
                "AM ID": {
                    "rich_text": [{"text": {"content": task.am_id}}]
                },
                "Task": {
                    "title": [{"text": {"content": task.title}}]
                },
                "Done": {
                    "checkbox": task.done
                }
            }

            # Add optional fields if they exist
            if task.time_estimate:
                fields["Estimated Duration (min)"] = {"number": task.time_estimate}

            if task.duration:
                fields["Tracked Time (min)"] = {"number": task.duration}

            if task.day:
                fields["Scheduled"] = {"date": {"start": task.day.date_only_if_time_is_midnight}}

            if task.planned_week:
                week_id = self._get_week_page_id_by_name(task.planned_week)
                fields["Planned Week"] = {"relation": [{"id": week_id}]}

            if task.planned_month:
                month_id = self._get_month_page_id_by_name(task.planned_month)
                fields["Planned Month"] = {"relation": [{"id": month_id}]}

            # Update the task in Notion
            self._update_database_page(task.notion_id, fields)
            print(f"Updated task in Notion: {task.title}")
        except Exception as e:
            print(f"Error updating task in Notion: {e}")
