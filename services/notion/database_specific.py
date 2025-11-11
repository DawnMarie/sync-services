from datetime import datetime

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

    def _get_task_pages_by_delete_checkbox(self) -> str | List[dict]:
        return self._get_database_pages_by_checkbox_field(self.tasks_database_id, "Delete", True)

    def _get_task_pages_by_scheduled_date(self, date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_date_field(self.tasks_database_id, "Scheduled", date)

    def _get_task_pages_by_title(self, task: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.tasks_database_id, "Task", task)

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

    def _get_activity_pages_by_date(self, page_date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_date_field(self.activity_database_id, "Date", page_date)

    def _get_pr_pages_by_title(self, pr: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.pr_database_id, "Record", pr)

    def _get_steps_pages_by_date(self, page_date: Timecube) -> str | List[dict]:
        return self._get_database_pages_by_date_field(self.steps_database_id, "Date", page_date)

    def _get_tracker_pages_by_title(self, tracker: str) -> str | List[dict]:
        return self._get_database_pages_by_title(self.tracker_database_id, "Name", tracker)

    def _get_tracker_data_most_recent(self):
        weight = self._get_database_pages_by_title(self.tracker_database_id, "Name", "Weight")[0]["properties"]["Current Value"]["formula"]["number"]
        bodyfat = self._get_database_pages_by_title(self.tracker_database_id, "Name", "Body Fat")[0]["properties"]["Current Value"]["formula"]["number"]
        heat_loan = self._get_database_pages_by_title(self.tracker_database_id, "Name", "HEAT Loan")[0]["properties"]["Current Value"]["formula"]["number"]
        credit_card = self._get_database_pages_by_title(self.tracker_database_id, "Name", "Credit Card")[0]["properties"]["Current Value"]["formula"]["number"]
        fed_student = self._get_database_pages_by_title(self.tracker_database_id, "Name", "Federal Student Loan")[0]["properties"]["Current Value"]["formula"]["number"]
        prim_mort = self._get_database_pages_by_title(self.tracker_database_id, "Name", "Primary Mortgage")[0]["properties"]["Current Value"]["formula"]["number"]
        sec_mort = self._get_database_pages_by_title(self.tracker_database_id, "Name", "Secondary Mortgage")[0]["properties"]["Current Value"]["formula"]["number"]

        weight = round(float(weight), 2)
        bodyfat = round(float(bodyfat), 2)
        return weight, bodyfat, heat_loan, credit_card, fed_student, prim_mort, sec_mort

    def _post_new_activity(self, activity: Activity):
        properties = self._create_activity_properties(activity)
        return self._post_new_database_page(self.activity_database_id, properties)

    def _post_new_mood(self, mood_date: Timecube, mood: str):
        page_title = f"Mood - {mood_date.date_for_titles}"
        properties = {
            "Mood": {"select": {"name": mood}},
            "Date": {"date": {"start": mood_date.date_Y_m_d}},
            "Name": {"title": [{"text": {"content": page_title}}]}
        }
        return self._post_new_database_page(self.mood_database_id, properties)

    def _post_new_week(self, week: str) -> dict:
        properties = {
            "Name": {
                "title": [{"text": {"content": week}}]
            }
        }
        return self._post_new_database_page(self.week_database_id, properties)

    def _post_new_month(self, month: str) -> dict:
        properties = {
            "Name": {
                "title": [{"text": {"content": month}}]
            }
        }
        return self._post_new_database_page(self.month_database_id, properties)

    def _post_new_quarter(self, quarter: str) -> dict:
        properties = {
            "Quarter": {
                "title": [{"text": {"content": quarter}}]
            }
        }
        return self._post_new_database_page(self.quarter_database_id, properties)

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
                "date": {
                    "start": project.day.date_only_if_time_is_midnight
                }
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
                "relation": goal_relation
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
        print(f"Creating subtask in Notion: {subtask.title}")
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
            properties = self._create_time_cycle_properties(task, properties)
        else:
            properties["Scheduled"] = {"date": None}
            properties = self._set_time_cycles(properties, task)

        if task.project:
            project_page = self._get_project_pages_by_title(task.project)
            if project_page == "No page returned!":
                project_id = self._post_new_project(Project(title=task.project))["id"]
            else:
                project_id = project_page[0]["id"]
            properties["Projects"] = {"relation": [{"id": project_id}]}

        if task.subcategory:
            value_goal_id = self._get_value_goal_pages_by_title(task.subcategory)[0]["id"]
            properties["Value Goals"] = {"relation": [{"id": value_goal_id}]}

        if task.pillar:
            pillar_id = self._get_pillar_pages_by_title(task.pillar)[0]["id"]
            properties["Pillar"] = {"relation": [{"id": pillar_id}]}

        if task.goal:
            goal_relation = []
            for goal in task.goal:
                goal_id = self._get_goal_outcome_pages_by_title(goal)[0]["id"]
                goal_relation.append({"id": goal_id})
            properties["Goal Outcome"] = {"relation": goal_relation}

        if task.tags:
            properties["Tags"] = {"multi_select": []}
            for tag in task.tags:
                properties["Tags"]["multi_select"].append({"name": tag})

        if task.done:
            status = "Done"
            properties["Done"] = {"checkbox": True}
        else:
            status = "Active"
            properties["Done"] = {"checkbox": False}
        properties["Status"] = {"status": {"name": status}}

        print(f"Creating task in Notion: {task}")
        return self._post_new_database_page(self.tasks_database_id, properties)

    def _post_new_body_fat_tracker_entry(self, timecube: Timecube, body_fat: float) -> dict:
        tracker_id = self._get_tracker_pages_by_title("Body Fat")[0]["id"]
        properties = {
            "Tracker Entry": {
                "title": [{"text": {"content": "Body Fat Log - " + timecube.date_for_titles}}]
            },
            "Date": {
                "date": {"start": timecube.date_Y_m_d}
            },
            "Value": {
                "number": body_fat
            },
            "Unit": {
                "rich_text": [{"text": {"content": "percent"}}]
            },
            "Tracker": {
                "relation": [{"id": tracker_id}]
            }
        }
        return self._post_new_database_page(self.tracker_entry_database_id, properties)

    def _post_new_weight_tracker_entry(self, timecube: Timecube, weight: float) -> dict:
        tracker_id = self._get_tracker_pages_by_title("Weight")[0]["id"]
        properties = {
            "Tracker Entry": {
                "title": [{"text": {"content": "Weight Log - " + timecube.date_for_titles}}]
            },
            "Date": {
                "date": {"start": timecube.date_Y_m_d}
            },
            "Value": {
                "number": weight
            },
            "Unit": {
                "rich_text": [{"text": {"content": "percent"}}]
            },
            "Tracker": {
                "relation": [{"id": tracker_id}]
            }
        }
        response = self._post_new_database_page(self.tracker_entry_database_id, properties)
        return response

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

    def _update_activity_page(self, activity: Activity, activity_page_id: str):
        properties = self._create_activity_properties(activity)
        return self._update_database_page(activity_page_id, properties)

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

    def _update_task(self, task: Task):
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

            if task.tags:
                properties["Tags"] = {"multi_select": []}
                for tag in task.tags:
                    properties["Tags"]["multi_select"].append({"name": tag})

            if task.day:
                properties = self._create_time_cycle_properties(task, properties)
            else:
                properties["Scheduled"] = {"date": None}
                properties = self._set_time_cycles(properties, task)

            # Update the task in Notion
            print(f"Updating task in Notion: {task}")
            return self._update_database_page(task.notion_id, properties)

        except Exception as e:
                print(f"Error updating task in Notion: {e}")
                return None

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

    def _add_dependency_to_project(self, project_id: str, dependency_title: str):
        dependency_id = self._get_project_pages_by_title(dependency_title)[0]["id"]
        properties = {
            "Dependent On": {
                "relation": [{"id": dependency_id}]
            }
        }
        return self._update_database_page(project_id, properties)

    def _add_subtask_to_task(self, subtask: Subtask, parent_id: str):
        subtask_id = self._post_new_subtask(subtask)["id"]
        properties = {
            "Sub-item": {
                "relation": [{"id": subtask_id}]
            }
        }
        print(f"Adding subtask {subtask.title} to task {parent_id} in Notion: ")
        return self._update_database_page(parent_id, properties)

    def _add_dependency_to_task(self, task_id: str, dependency_title: str):
        dependency_id = self._get_task_pages_by_title(dependency_title)[0]["id"]
        properties = {
            "Dependent On": {
                "relation": [{"id": dependency_id}]
            }
        }
        print(f"Adding dependency {dependency_title} to task {task_id} in Notion")
        return self._update_database_page(task_id, properties)

    @staticmethod
    def _create_activity_properties(activity):
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
        return properties

    def _create_time_cycle_properties(self, task, properties):
            today = Timecube.from_datetime(datetime.today())
            is_today = task.day.date_in_datetime.date() == today.date_in_datetime.date()
            is_work = (task.project == "Meetings") or (task.project == "Andover")
            if is_today and not is_work:
                week_title = f"Week {today.week_number}<<"
                month_title = f"{today.date_M_Y}<<"
                quarter_title = f"Q{today.quarter} {today.date_in_datetime.year}<<"

                daily_tracking_id = self._get_daily_tracking_pages_by_date(task.day)[0]["id"]
                week_id = self._get_week_pages_by_title(week_title)[0]["id"]
                month_id = self._get_month_pages_by_title(month_title)[0]["id"]
                quarter_id = self._get_quarter_pages_by_title(quarter_title)[0]["id"]

                properties["Scheduled"] = {"date": {"start": task.day.date_only_if_time_is_midnight}}
                properties["Daily Tracking"] = {"relation": [{"id": daily_tracking_id}]}
                properties["Planned Week"] = {"relation": [{"id": week_id}]}
                properties["Planned Month"] = {"relation": [{"id": month_id}]}
                properties["Planned Quarter"] = {"relation": [{"id": quarter_id}]}

            else:
                properties["Scheduled"] = {"date": {"start": task.day.date_only_if_time_is_midnight}}
                properties = self._set_time_cycles(properties, task)

            return properties

    def _set_time_cycles(self, properties, task) -> dict:
        if task.planned_week:
            week_page = self._get_week_pages_by_title(task.planned_week)
            if week_page == "No page returned!":
                week_page_id = self._post_new_week(task.planned_week)["id"]
            else:
                week_page_id = week_page[0]["id"]
            properties["Planned Week"] = {"relation": [{"id": week_page_id}]}
        else:
            properties["Planned Week"] = {"relation": []}
        if task.planned_month:
            month_page = self._get_month_pages_by_title(task.planned_month)
            if month_page == "No page returned!":
                month_page_id = self._post_new_month(task.planned_month)["id"]
            else:
                month_page_id = month_page[0]["id"]
            properties["Planned Month"] = {"relation": [{"id": month_page_id}]}
        else:
            properties["Planned Month"] = {"relation": []}
        if task.planned_quarter:
            quarter_page = self._get_quarter_pages_by_title(task.planned_quarter)
            if quarter_page == "No page returned!":
                quarter_page_id = self._post_new_quarter(task.planned_quarter)["id"]
            else:
                quarter_page_id = quarter_page[0]["id"]
            properties["Planned Quarter"] = {"relation": [{"id": quarter_page_id}]}
        return properties
