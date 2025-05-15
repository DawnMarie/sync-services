from data_models.activity import Activity
from data_models.project import Project
from data_models.sleep import Sleep
from data_models.subtask import Subtask
from data_models.task import Task
from data_models.timecube import Timecube
from services.notion.database_fields import NotionDatabaseFields

from typing import List
"""
GET/POST/PATCH methods for specific databases
"""


class NotionDatabaseSpecific(NotionDatabaseFields):
    """
    GET/POST/PATCH specific database pages
    """
    def _get_pillar_pages_by_title(self, pillar: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.pillar_database_id, "Pillar", pillar)

    def _get_value_goal_pages_by_title(self, value_goal: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.value_goal_database_id, "Name", value_goal)

    def _get_goal_outcome_page_by_id(self, goal_id: str) -> str | dict:
        return self._get_page_by_id(goal_id)

    def _get_goal_outcome_pages_by_title(self, goal: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.goal_outcome_database_id, "Name", goal)

    def _get_project_pages_by_title(self, project: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.project_database_id, "Project Name", project)

    def _get_task_pages_by_am_id(self, am_id: str) -> str | List[dict]:
        return self._get_database_pages_by_text_field(self.tasks_database_id, "AM ID", am_id)

    def _get_task_pages_by_title(self, task: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.tasks_database_id, "Title", task)

    def _get_task_pages_by_last_edited(self, minutes_in_the_past: int) -> str | List[dict]:
        return self._get_database_pages_by_last_edited(self.tasks_database_id, minutes_in_the_past)

    def _get_quarter_pages_by_title(self, quarter: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.quarter_database_id, "Quarter", quarter)

    def _get_month_pages_by_title(self, month: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.month_database_id, "Name", month)

    def _get_week_pages_by_title(self, week: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.week_database_id, "Name", week)

    def _get_daily_tracking_pages_by_date(self, date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_date_field(self.daily_tracking_database_id, "Date", date)

    def _get_daily_tracking_pages_by_title(self, todays_page: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.daily_tracking_database_id, "Today's Page", todays_page)

    def _get_fitness_stats_pages_by_date(self, page_date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_date_field(self.stats_database_id, "Today's Date", page_date)

    def _get_pr_pages_by_title(self, pr: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.pr_database_id, "Record", pr)

    def _get_steps_pages_by_date(self, page_date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_date_field(self.steps_database_id, "Date", page_date)

    def _get_stepbet_pages_by_start_and_end_date(self, start_date: Timecube, end_date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_start_and_end_date_field(self.stepbet_database_id, start_date, end_date)

    def _post_new_activity(self, activity: Activity):
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
        return self._post_new_database_page(self.activity_database_id, properties)

    def _post_new_mood(self, mood_date: Timecube, mood: str):
        page_title = f"Mood - {mood_date.date_for_titles}"
        properties = {
            "Mood": {"select": {"name": mood}},
            "Date": {"date": {"start": mood_date.date_Y_m_d}},
            "Name": {"title": [{"text": {"content": page_title}}]}
        }
        return self._post_new_database_page(self.mood_database_id, properties)

    def _post_new_project(self, project: Project) -> dict:
        pillar_id = self._get_pillar_pages_by_title(project.pillar)[0]["id"]
        properties = {
            "Project Name": {
                "title": [{"text": {"content": project.title}}]
            },
            "Pillars": {
                "relation": [{"id": pillar_id}]
            }
        }

        if project.am_id:
            properties["AM ID"] = {
                "rich_text": [{"text": {"content": project.am_id}}]
            }

        if project.day:
            properties["Review Date"] = {
                "date": {"start": project.day.date_only_if_time_is_midnight}
            }

        if project.subcategory:
            value_goal_id = self._get_value_goal_pages_by_title(project.subcategory)[0]["id"]
            properties["Value Goals"] = {
                "relation": [{"id": value_goal_id}]
            }

        if project.goal:
            goal_relation = []
            for goal in project.goal:
                goal_id = self._get_goal_outcome_pages_by_title(goal)[0]["id"]
                goal_relation.append({"id": goal_id})
            properties["Goal Outcomes"] = {
                "relation": [{"id": goal_relation}]
            }

        if project.planned_week:
            week_id = self._get_week_pages_by_title(project.planned_week)[0]["id"]
            properties["Planned Week"] = {
                "relation": [{"id": week_id}]
            }

        if project.planned_month:
            month_id = self._get_month_pages_by_title(project.planned_month)[0]["id"]
            properties["Planned Month"] = {
                "relation": [{"id": month_id}]
            }

        if project.planned_quarter:
            quarter_id = self._get_quarter_pages_by_title(project.planned_quarter)[0]["id"]
            properties["Planned Quarter"] = {
                "relation": [{"id": quarter_id}]
            }

        return self._post_new_database_page(self.project_database_id, properties)

    def _post_new_sleep(self, sleep: Sleep, skip_zero_sleep=True) -> dict | str:
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
                "rich_text": [{"text": {"content": Sleep.format_hours_to_hm(sleep.total_sleep)}}]},
            "Light Sleep": {
                "rich_text": [{"text": {"content": Sleep.format_hours_to_hm(sleep.light_sleep)}}]},
            "Deep Sleep": {
                "rich_text": [{"text": {"content": Sleep.format_hours_to_hm(sleep.deep_sleep)}}]},
            "REM Sleep": {
                "rich_text": [{"text": {"content": Sleep.format_hours_to_hm(sleep.rem_sleep)}}]},
            "Awake Time": {
                "rich_text": [{"text": {"content": Sleep.format_hours_to_hm(sleep.awake_time)}}]},
            "Resting HR": {"number": sleep.resting_hr if hasattr(sleep, 'resting_hr') else 0}
        }
        return self._post_new_database_page(self.sleep_database_id, properties)

    def _post_new_steps(self, entry_date: Timecube, steps: int, total_distance: int):
        """Add a new page to the Step Database with the day's steps. Returns the id of the created page"""
        properties_payload = {
            "Activity": {
                "title": [{"text": {"content": "Walking - " + entry_date.date_for_titles}}]
            },
            "Date": {
                "date": {"start": entry_date.date_Y_m_d}
            },
            "Total Steps": {
                "number": steps
            },
            "Total Distance (miles)": {
                "number": total_distance
            }
        }
        return self._post_new_database_page(self.steps_database_id, properties_payload)

    def _post_new_subtask(self, subtask: Subtask) -> dict:
        if subtask.done:
            status = "Done"
        else:
            status = "Active"
        properties = {
            "Task": {
                "title": [{"text": {"content": subtask.title}}]
            },
            "AM ID": {
                "rich_text": [{"text": {"content": subtask.am_id}}]
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
        return self._post_new_database_page(self.tasks_database_id, properties)

    def _post_new_task(self, task: Task) -> dict:
        properties = {
            "Task": {
                "id": "title",
                "title": [{"text": {"content": task.title}}]
            },
            "AM ID": {
                "rich_text": [{"text": {"content": task.am_id}}]
            },
            "Tracked Time (min)": {
                "number": task.duration
            },
            "Estimated Duration (min)": {
                "number": task.time_estimate
            },
        }

        if task.day:
            properties["Scheduled"] = {
                "date": {"start": task.day.date_only_if_time_is_midnight}
            }

        if task.project:
            project_id = self._get_project_pages_by_title(task.project)[0]["id"]
            properties["Projects"] = {
                "relation": [{"id": project_id}]
            }

        if task.subcategory:
            value_goal_id = self._get_value_goal_pages_by_title(task.subcategory)[0]["id"]
            properties["Value Goal"] = {
                "relation": [{"id": value_goal_id}]
            }

        if task.pillar:
            pillar_id = self._get_pillar_pages_by_title(task.pillar)[0]["id"]
            properties["Pillar"] = {
                "relation": [{"id": pillar_id}]
            }

        if task.goal:
            goal_relation = []
            for goal in task.goal:
                goal_id = self._get_goal_outcome_pages_by_title(goal)[0]["id"]
                goal_relation.append({"id": goal_id})
            properties["Goal Outcome (DB)"] = {"relation": [{"id": goal_relation}]}

        if task.planned_week:
            week_id = self._get_week_pages_by_title(task.planned_week)[0]["id"]
            properties["Planned Week"] = {
                "relation": [{"id": week_id}]
            }

        if task.planned_month:
            month_id = self._get_month_pages_by_title(task.planned_month)[0]["id"]
            properties["Planned Month"] = {
                "relation": [{"id": month_id}]
            }

        if task.planned_quarter:
            quarter_id = self._get_quarter_pages_by_title(task.planned_quarter)[0]["id"]
            properties["Planned Quarter"] = {
                "relation": [{"id": quarter_id}]
            }

        if task.tags:
            properties["Tags"] = {"multi_select": []}
            for tag in task.tags:
                properties["Tags"]["multi_select"].append({"name": tag})

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

        return self._post_new_database_page(self.tasks_database_id, properties)

    def _post_new_training_page(self, timecube: Timecube, training_status: str, readiness_description: str,
                                training_readiness: int, daily_average_stress: int):
        properties = {
            "Training Log": {
                "title": [{"text": {"content": "Training Log - " + timecube.date_for_titles}}]
            },
            "Today's Date": {
                "date": {"start": timecube.date_Y_m_d}
            },
            "Training Status": {
                "rich_text": [{"text": {"content": training_status}}]
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
        }
        return self._post_new_database_page(self.stats_database_id, properties)

    def _update_daily_tracking_page(self, timecube: Timecube, field: str, field_type: str, value: str | int):
        page_id = self._get_daily_tracking_pages_by_date(timecube)[0]["id"]
        properties = {
            field: {field_type: value}
        }
        return self._update_database_page(page_id, properties)

    def _update_steps_page_with_steps(self, timecube: Timecube, steps: int, total_distance: int):
        page_id = self._get_steps_pages_by_date(timecube)[0]["id"]
        properties = {
            "Total Steps": {
                "number": steps
            },
            "Total Distance (miles)": {
                "number": total_distance
            }
        }
        return self._update_database_page(page_id, properties)

    def _update_steps_page_with_stepbet_links(self, timecube: Timecube, stepbet_links: List[str]):
        page_id = self._get_steps_pages_by_date(timecube)[0]["id"]
        links_payload = []
        for item in stepbet_links:
            links_payload.append({'id': item})
        properties = {
            "StepBet Link": {
                "relation": links_payload
            }
        }
        return self._update_database_page(page_id, properties)

    def _update_task(self, task: Task) -> None:
        """
        Update a task in Notion.
        """
        try:
            # Create a dictionary of properties to update
            properties = {
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

            # Add optional properties if they exist
            if task.time_estimate:
                properties["Estimated Duration (min)"] = {"number": task.time_estimate}

            if task.duration:
                properties["Tracked Time (min)"] = {"number": task.duration}

            if task.day:
                properties["Scheduled"] = {"date": {"start": task.day.date_only_if_time_is_midnight}}

            if task.planned_week:
                week_id = self._get_week_pages_by_title(task.planned_week)
                properties["Planned Week"] = {"relation": [{"id": week_id}]}

            if task.planned_month:
                month_id = self._get_month_pages_by_title(task.planned_month)
                properties["Planned Month"] = {"relation": [{"id": month_id}]}

            if task.tags:
                properties["Tags"] = {"multi_select": []}
                for tag in task.tags:
                    properties["Tags"]["multi_select"].append({"name": tag})

            # Update the task in Notion
            self._update_database_page(task.notion_id, properties)
            print(f"Updated task in Notion: {task.title}")
        except Exception as e:
            print(f"Error updating task in Notion: {e}")

    def _update_training_page(
            self, timecube: Timecube, training_status: str, readiness_description: str,
            training_readiness: int, daily_average_stress: int):
        page_id = self._get_fitness_stats_pages_by_date(timecube)[0]["id"]
        properties = {
            "Training Status": {"rich_text": [{"text": {"content": training_status}}]},
            "Readiness Score": {"number": training_readiness},
            "Readiness Description": {"rich_text": [{"text": {"content": readiness_description}}]},
            "Average Stress": {"number": daily_average_stress}
        }
        return self._update_database_page(page_id, properties)

    def _add_subtask_to_task(self, subtask: Subtask, parent_id: str):
        subtask_id = self._post_new_subtask(subtask)
        properties = {
            "Sub-item": {
                "relation": [{"id": subtask_id}]
            }
        }
        return self._update_database_page(parent_id, properties)

    def _add_dependency_to_task(self, task_id: str, dependency_title: str):
        dependency_id = self._get_task_pages_by_title(dependency_title)[0]["id"]
        properties = {
            "Dependent On": {
                "relation": [{"id": dependency_id}]
            }
        }
        return self._update_database_page(task_id, properties)
