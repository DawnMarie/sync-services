from data_models.activity import Activity
from data_models.insight import Insight
from data_models.personal_record import PR
from data_models.sleep import Sleep
from data_models.task import Task
from data_models.timecube import Timecube
from services.notion.page_specific import NotionPageSpecific
from services.notion.database_specific import NotionDatabaseSpecific
from services.notion.transformer import NotionTransformer

from datetime import date, datetime, timedelta
from typing import List

import os

class NotionManager(NotionPageSpecific, NotionTransformer):

    def get_current_stepbet_games(self):
        """
        Pull the page ids of the current StepBet games so that the step goal
        can be pulled into the Garmin Daily Steps database
        :return:
        """
        today_timecube = Timecube.from_datetime(datetime.today())
        return self._get_stepbet_pages_by_start_and_end_date(self, today_timecube, today_timecube)

    def get_habits_from_daily_tracking_page_by_date(self, timecube: Timecube):
        habit_object = {}
        daily_tracking_page = self._get_daily_tracking_pages_by_date(timecube)[0]
        habits = os.getenv("HABITS").split(",")
        for habit in habits:
            is_checked = daily_tracking_page["properties"][habit]["checkbox"]
            habit_object[habit] = is_checked
        return habit_object

    def get_tasks_for_sync(self, am_id_list: List):
        tasks_to_compare = []
        tasks_not_found = []
        for task_id in am_id_list:
            task_pages = self._get_task_pages_by_am_id(task_id)
            if task_pages[0]:
                task_dto = self._convert_task_response_to_dto(task_pages[0])
                tasks_to_compare.append(task_dto)
            else:
                tasks_not_found.append(task_id)
        return tasks_to_compare, tasks_not_found

    def create_activity_page(self, activity: Activity) -> dict:
        activity_id = self._post_new_activity(activity)
        icon = {"type": "external", "external": {"url": activity.icon}}
        return self._update_page_icon(activity_id, icon)

    def create_sleep_page(self, sleep: Sleep):
        sleep_id = self._post_new_sleep(sleep)
        icon = {"emoji": "😴"}
        return self._update_page_icon(sleep_id, icon)

    def create_task_with_subtasks(self, task: Task) -> str:
        task_id = self._post_new_task(task)
        if task.subtasks:
            for subtask in task.subtasks:
                task_id = self._add_subtask_to_task(subtask, task_id)
        return task_id

    def create_today_training_page(self, training_status: str, training_readiness: int,
                                   training_description: str, daily_average_stress: int):
        timecube = Timecube.from_datetime(datetime.today())
        return self._post_new_training_page(
            timecube, training_status, training_description, training_readiness, daily_average_stress)

    def update_calories_out_in_daily_tracking(self, timecube: Timecube, calories_out: int):
        return self._update_daily_tracking_page(timecube, "Calories Out", "number", calories_out)

    def update_daily_insights_block(self, daily_insights: List[Insight]):
        block_ids = self._get_block_children_by_id(self.insight_block_id)
        title_change_response = self._update_block_text(datetime.today().strftime('%A') + " Insights", block_ids[0], "heading_1")
        insight_responses = [self._update_daily_insight(daily_insights[0], block_ids[1], block_ids[2]),
                             self._update_daily_insight(daily_insights[1], block_ids[3], block_ids[4]),
                             self._update_daily_insight(daily_insights[2], block_ids[5], block_ids[6]),
                             self._update_weekly_insight(daily_insights[3], block_ids[8], block_ids[9]),
                             self._update_weekly_insight(daily_insights[4], block_ids[10], block_ids[11]),
                             self._update_weekly_insight(daily_insights[5], block_ids[12], block_ids[13])]
        return title_change_response, insight_responses

    def update_menstrual_cycle_for_today(self, menstrual_cycle_day: int):
        today_timecube = Timecube.from_datetime(datetime.today())
        return self._update_daily_tracking_page(today_timecube, "Cycle Day", "number", menstrual_cycle_day)

    def update_mood_in_daily_tracking_and_mood_tracker(self, mood: int):
        yesterday_timecube = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        mood_str = self._convert_mood_int_to_str(mood)
        daily_mood_response = self._update_daily_tracking_page(yesterday_timecube, "Mood", "select", {"name": mood_str})
        mood_tracker_response = self._post_new_mood(yesterday_timecube, mood_str)
        return daily_mood_response, mood_tracker_response

    def update_daily_note_for_yesterday(self, daily_note: str):
        yesterday_timecube = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        daily_note = [{"text": {"content": daily_note}}]
        return self._update_daily_tracking_page(yesterday_timecube, "Daily Note", "rich_text", daily_note)

    def update_mobile_screen_time_for_yesterday(self, mobile_screen_time):
        yesterday_timecube = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        return self._update_daily_tracking_page(
            yesterday_timecube, "Mobile Screen Time (min)", "number", mobile_screen_time)

    def update_pr_entry(self, record: PR):
        page_id = self._get_pr_pages_by_title(record.activity_name)[0]["id"]
        properties = {
            "Date": {"date": {"start": record.activity_date.date_time_Y_m_d_H_M_S}},
            "PR": {"checkbox": True}
        }

        if record.value:
            properties["Value"] = {"rich_text": [{"text": {"content": record.value}}]}
        if record.pace:
            properties["Pace"] = {"rich_text": [{"text": {"content": record.pace}}]}

        icon = {"emoji": record.icon}

        return (self._update_database_page(page_id, properties),
                self._update_page_icon(page_id, icon))

    def update_steps_entries_for_today(self, steps: int, total_distance: int):
        """
        Update existing step counts
        """
        today_timecube = Timecube.from_datetime(datetime.today())
        dt_steps_response = self._update_daily_tracking_page(today_timecube, "Steps", "number", steps)
        steps_response = self._update_steps_page_with_steps(today_timecube, steps, total_distance)
        return dt_steps_response, steps_response

    def update_task_dependencies(self, task: Task) -> str:
        task_id = ""
        for dependency in task.depends_on:
            task_id = self._add_dependency_to_task(task_id, dependency)
        return task_id

    def update_training_entries_for_today(self, training_status: str, training_readiness: int,
                                          readiness_description: str, daily_average_stress: int):
        today_timecube = Timecube.from_datetime(datetime.today())
        # update Daily Tracking Page
        status_properties = [{"text": {"content": training_status}}]
        readiness_properties = [{"text": {"content": readiness_description}}]
        status_daily_response = self._update_daily_tracking_page(
            today_timecube, "Training Status", "rich_text", status_properties)
        readiness_daily_response = self._update_daily_tracking_page(
            today_timecube, "Readiness Score", "number", training_readiness)
        description_daily_response = self._update_daily_tracking_page(
            today_timecube, "Readiness Description", "rich_text", readiness_properties)
        stress_daily_response = self._update_daily_tracking_page(
            today_timecube, "Average Stress", "number", daily_average_stress)

        # update Stats Page for day
        stats_response = self._update_training_page(
            today_timecube, training_status, readiness_description, training_readiness, daily_average_stress)

        return status_daily_response, readiness_daily_response, \
            description_daily_response, stress_daily_response, stats_response

    def update_training_entries_for_yesterday(self, training_status: str, training_readiness: int,
                                          readiness_description: str, daily_average_stress: int):
        yesterday_timecube = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        # update Daily Tracking Page
        status_properties = [{"text": {"content": training_status}}]
        readiness_properties = [{"text": {"content": readiness_description}}]
        status_daily_response = self._update_daily_tracking_page(
            yesterday_timecube, "Training Status", "rich_text", status_properties)
        readiness_daily_response = self._update_daily_tracking_page(
            yesterday_timecube, "Readiness Score", "number", training_readiness)
        description_daily_response = self._update_daily_tracking_page(
            yesterday_timecube, "Readiness Description", "rich_text", readiness_properties)
        stress_daily_response = self._update_daily_tracking_page(
            yesterday_timecube, "Average Stress", "number", daily_average_stress)

        # update Stats Page for day
        stats_response = self._update_training_page(
            yesterday_timecube, training_status, readiness_description, training_readiness, daily_average_stress)

        return status_daily_response, readiness_daily_response, \
            description_daily_response, stress_daily_response, stats_response

    def update_weight_bodyfat_for_today(self, weight: int, body_fat: int):
        today_timecube = Timecube.from_datetime(datetime.today())
        weight_daily_response = self._update_daily_tracking_page(today_timecube, "Weight", "number", weight)
        bf_daily_response = self._update_daily_tracking_page(today_timecube, "Body Fat", "number", body_fat)
        return weight_daily_response, bf_daily_response

