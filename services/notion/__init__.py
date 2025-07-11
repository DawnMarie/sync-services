from data_models.activity import Activity
from data_models.insight import Insight
from data_models.personal_record import PR
from data_models.project import Project
from data_models.sleep import Sleep
from data_models.task import Task
from data_models.timecube import Timecube
from services.notion.page_specific import NotionPageSpecific
from services.notion.database_specific import NotionDatabaseSpecific
from services.notion.transformer import NotionTransformer

from datetime import datetime, timedelta
from typing import List, Tuple

import os

class NotionManager(NotionPageSpecific, NotionTransformer):

    def get_current_stepbet_games(self):
        """
        Pull the page ids of the current StepBet games so that the step goal
        can be pulled into the Garmin Daily Steps database
        :return:
        """
        today_timecube = Timecube.from_datetime(datetime.today())
        return self._get_stepbet_pages_by_start_and_end_date(today_timecube, today_timecube)

    def get_habits_from_daily_tracking_page_by_date(self, timecube: Timecube) -> dict | str:
        habit_object = {}
        daily_tracking_page = self._get_daily_tracking_pages_by_date(timecube)[0]
        habits = os.getenv("HABITS").split(",")
        for habit in habits:
            is_checked = daily_tracking_page["properties"][habit]["checkbox"]
            habit_object[habit] = is_checked
        return habit_object

    def get_tasks_by_scheduled(self, scheduled_date: Timecube) -> List[Task]:
        task_pages = self._get_task_pages_by_scheduled_date(scheduled_date)
        task_dtos = []
        if task_pages == "No page returned!":
            return []
        for page in task_pages:
            task = self._convert_task_response_to_dto(page)
            task_dtos.append(task)
        return task_dtos

    def get_tasks_completed_by_date(self, timecube: Timecube) -> List[Task]:
        task_pages = self._get_task_pages_by_scheduled_date(timecube)
        task_dtos = []
        if task_pages == "No page returned!":
            return []
        for page in task_pages:
            if page["properties"]["Done"]["checkbox"]:
                task = self._convert_task_response_to_dto(page)
                task_dtos.append(task)
        return task_dtos

    def get_task_for_compare_and_sync(self, am_id: str) -> Task | str:
        task_page = self._get_task_pages_by_am_id(am_id)
        if task_page != "No page returned!":
            task_dto = self._convert_task_response_to_dto(task_page[0])
            return task_dto
        else:
            return task_page

    def get_tasks_for_date_and_next_6_days(self, start_date: Timecube) -> Tuple[List[Task], List[Task]]:
        """
        Get tasks scheduled for a specific day and tasks scheduled for that day plus the next 6 days.

        Args:
            start_date: The specific day to start from

        Returns:
            A tuple containing two lists:
            - List of tasks scheduled for the specific day
            - List of tasks scheduled for the specific day and the next 6 days
        """
        # Get tasks for the specific day
        tasks_for_day = self._get_task_pages_by_scheduled_date(start_date)
        tasks_for_day_list = []

        if tasks_for_day != "No page returned!":
            for page in tasks_for_day:
                tasks_for_day_list.append(page)

        # Get tasks for the next 7 days (including the specific day)
        end_date = Timecube.from_datetime(start_date.date_in_datetime + timedelta(days=6))
        start_date = Timecube.from_datetime(start_date.date_in_datetime + timedelta(days=1))
        tasks_for_week_list = tasks_for_day_list.copy()
        while start_date.date_in_datetime <= end_date.date_in_datetime:
            tasks_for_week = self._get_task_pages_by_scheduled_date(start_date)
            if tasks_for_week != "No page returned!":
                for page in tasks_for_week:
                    tasks_for_week_list.append(page)
            start_date = Timecube.from_datetime(start_date.date_in_datetime + timedelta(days=1))

        return tasks_for_day_list, tasks_for_week_list

    def get_tasks_to_delete(self) -> List[Task]:
        """
        Get tasks with the Delete checkbox checked.
        """
        task_pages = self._get_task_pages_by_delete_checkbox()
        if task_pages == "No page returned!":
            return []

        tasks = []
        for page in task_pages:
            task = self._convert_task_response_to_dto(page)
            tasks.append(task)

        return tasks

    def delete_task(self, task: Task):
        return self._delete_page_by_id(task.notion_id)

    def create_or_update_activity_page(self, activity: Activity) -> dict | str:
        does_activity_exist = self._get_activity_pages_by_date(activity.activity_date)
        if does_activity_exist == "No page returned!":
            activity_id = self._post_new_activity(activity)["id"]
            icon = {"type": "external", "external": {"url": activity.icon}}
            return self._update_page_icon(activity_id, icon)
        else:
            # Flag to track if we found a matching activity
            matching_activity_found = False

            for page in does_activity_exist:
                notion_activity = Activity.from_notion_json(page)
                # Compare each notion page to garmin activity
                if not activity.is_different_than(notion_activity):
                    # Found a match, no need to create or update
                    matching_activity_found = True
                    return page

            # If no matching activity was found, create a new one
            if not matching_activity_found:
                activity_id = self._post_new_activity(activity)["id"]
                icon = {"type": "external", "external": {"url": activity.icon}}
                return self._update_page_icon(activity_id, icon)

            # This line should not be reached, but keeping it for safety
            return does_activity_exist

    def create_project_page(self, project: Project):
        return self._post_new_project(project)

    def create_sleep_page(self, sleep: Sleep):
        sleep_id = self._post_new_sleep(sleep)["id"]
        icon = {"emoji": "😴"}
        return self._update_page_icon(sleep_id, icon)

    def create_steps_page(self, timecube: Timecube, steps: int, total_distance: int):
        return self._post_new_steps(timecube, steps, total_distance)["id"]

    def create_task_with_subtasks(self, task: Task) -> str:
        task_id = self._post_new_task(task)["id"]
        if task.subtasks:
            for subtask in task.subtasks:
                task_id = self._add_subtask_to_task(subtask, task_id)["id"]
        return task_id

    def create_today_training_page(self, training_status: str, training_readiness: int,
                                   training_description: str, daily_average_stress: int):
        timecube = Timecube.from_datetime(datetime.today())
        return self._post_new_training_page(
            timecube, training_status, training_description, training_readiness, daily_average_stress)

    def update_calories_out_in_daily_tracking(self, timecube: Timecube, calories_out: int):
        return self._update_daily_tracking_page(timecube, "Calories Out", "number", calories_out)

    def update_daily_insights_block(self, daily_insights: List[Insight]):
        blocks = self._get_block_children_by_id(self.insight_block_id)
        title_change_response = self._update_block_text(datetime.today().strftime('%A') + " Insights", blocks[0]["id"], "heading_1")

        block_number = 1
        insight_number = 0
        insight_responses = []

        while insight_number < len(daily_insights) and block_number < len(blocks):
            insight = daily_insights[insight_number]

            # 2. Daily insight: update heading_2/heading_3
            if insight.insight_type == "Daily":
                if (block_number + 1 < len(blocks) and
                        blocks[block_number]["type"] == "heading_2" and
                        blocks[block_number + 1]["type"] == "heading_3"):
                    response = self._update_daily_insight(insight, blocks[block_number]["id"], blocks[block_number + 1]["id"])
                    insight_responses.append(response)
                    block_number += 2
                    insight_number += 1
                else:
                    block_number += 1  # Skip to next block if types don't match
            # 2a. Weekly insight: clear heading_2/heading_3 until divider
            elif insight.insight_type == "Weekly":
                while (block_number < len(blocks) and blocks[block_number]["type"] == "heading_2"):
                    self._update_block_text("", blocks[block_number]["id"], "heading_2")
                    self._update_block_text("", blocks[block_number]["id"], "heading_3")
                    block_number += 2
                # 3. Update heading_3/paragraph for weekly insight
                while (block_number + 1 < len(blocks) and
                       blocks[block_number]["type"] == "heading_3" and
                       blocks[block_number + 1]["type"] == "paragraph"):
                    response = self._update_weekly_insight(insight, blocks[block_number]["id"], blocks[block_number + 1]["id"])
                    insight_responses.append(response)
                    block_number += 2
                    insight_number += 1
                    break  # Only one weekly insight per block pair
                else:
                    block_number += 1
            else:
                block_number += 1

        # 4. Clear out any remaining blocks
        while block_number < len(blocks):
            block = blocks[block_number]
            if block["type"] in ("heading_2", "heading_3", "paragraph"):
                self._update_block_text("", block["id"], block["type"])
                block_number += 1
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

    def update_project_dependencies(self, project: Project):
        project_id = ""
        for dependency in project.depends_on:
            project_id = self._add_dependency_to_project(project, dependency)["id"]
        return project_id


    def update_steps_entries_for_today(self, steps: int, total_distance: int):
        """
        Update existing step counts
        """
        today_timecube = Timecube.from_datetime(datetime.today())
        dt_steps_response = self._update_daily_tracking_page(today_timecube, "Steps", "number", steps)
        steps_response = self._update_steps_page_with_steps(today_timecube, steps, total_distance)
        return dt_steps_response, steps_response

    def update_steps_page_with_stepbet_games(self, timecube: Timecube):
        game_ids = []
        game_pages = self.get_current_stepbet_games()
        for game in game_pages:
            game_ids.append(game["id"])
        return self._update_steps_page_with_stepbet_links(timecube, game_ids)

    def update_task_dependencies(self, task: Task) -> str:
        task_id = ""
        for dependency in task.depends_on:
            task_id = self._add_dependency_to_task(task.notion_id, dependency)["id"]
        return task_id

    def update_task_with_subtasks(self, task: Task) -> str:
        task_page = self._update_task(task)
        task_id = task_page["id"]
        if task.subtasks:
            for subtask in task.subtasks:
                task_id = self._add_subtask_to_task(subtask, task_id)
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

    def update_weight_bodyfat_hrv_for_today(self, weight: int, body_fat: int, hrv: int):
        today_timecube = Timecube.from_datetime(datetime.today())
        weight_daily_response = self._update_daily_tracking_page(today_timecube, "Weight", "number", weight)
        bf_daily_response = self._update_daily_tracking_page(today_timecube, "Body Fat", "number", body_fat)
        hrv_daily_response = self._update_daily_tracking_page(today_timecube, "HRV", "number", hrv)
        return weight_daily_response, bf_daily_response, hrv_daily_response
