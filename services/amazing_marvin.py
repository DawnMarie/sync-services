import base64
import sys

from data_models.project import Project
from data_models.subtask import Subtask
from data_models.task import Task
from data_models.timecube import Timecube

from couchdb import Server
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Any
import calendar
import os
import re
import requests
import time
import urllib.parse


class AmazingMarvinService:
    load_dotenv()

    def __init__(self):
        self.json_header = 'application/json'
        self.full_access_token = self._ensure_proper_encoding(os.getenv("AM_FULL_ACCESS_TOKEN"))
        self.sync_server = os.getenv("AM_SYNC_SERVER")
        self.sync_database = os.getenv("AM_SYNC_DATABASE")
        self.sync_user = os.getenv("AM_SYNC_USER")
        self.sync_password = os.getenv("AM_SYNC_PASSWORD")

        self.api_url = 'https://serv.amazingmarvin.com/api/'
        self.api_headers = {'X-Full-Access-Token': self.full_access_token}
        self.database_url = f"https://{self.sync_user}:{self.sync_password}@{self.sync_server}"

        # Add cache dictionaries
        self._project_cache = {}  # Cache for projects by ID
        self._goal_cache = {}     # Cache for goals by ID
        self._label_cache = None  # Cache for all labels (will be populated on first use)

        try:
            parsed_url = urllib.parse.urlparse(self.database_url)
            print(f"Connecting to server: {parsed_url.hostname}")
            print(f"Using database: {self.sync_database}")
            print(f"Protocol: {parsed_url.scheme}")

            # Add exception handling with full traceback
            import traceback
            try:
                self.couch = Server(self.database_url)
                self.db = self.couch[self.sync_database]
            except Exception as e:
                print("Full error traceback:")
                print(traceback.format_exc())

                # Specifically, check for URL encoding issues
                try:
                    # Try to manually encode components
                    encoded_user = urllib.parse.quote(self.sync_user, safe='')
                    encoded_password = urllib.parse.quote(self.sync_password, safe='')
                    encoded_url = f"https://{encoded_user}:{encoded_password}@{self.sync_server}"
                    print("\nAttempting connection with explicitly encoded URL...")
                    self.couch = Server(encoded_url)
                    self.db = self.couch[self.sync_database]
                except Exception as e2:
                    print("\nSecond attempt failed:")
                    print(traceback.format_exc())

                    # Print character encoding information
                    print("\nDebug information:")
                    print(f"Python's default encoding: {sys.getdefaultencoding()}")
                    print(f"Environment LANG: {os.getenv('LANG')}")
                    print(f"Environment LC_ALL: {os.getenv('LC_ALL')}")
                    print(f"Environment PYTHONIOENCODING: {os.getenv('PYTHONIOENCODING')}")

                    raise ConnectionError(f"Failed to connect to database after multiple attempts: {str(e2)}")
        except Exception as outer_e:
            print(f"Outer exception: {str(outer_e)}")
            raise

    @staticmethod
    def _ensure_proper_encoding(token):
        """Ensure the token is properly encoded regardless of environment"""
        if token is None:
            return None

        # Try to handle the token as base64 if it appears to be base64-encoded
        if '/' in token or '+' in token or '=' in token:
            try:
                # Decode and re-encode to ensure consistent format
                # This helps normalize tokens across environments
                decoded = base64.b64decode(token.encode('utf-8'))
                return base64.b64encode(decoded).decode('utf-8')
            except Exception:
                # If decoding fails, return the original token
                pass

        return token

    @staticmethod
    def _handle_request_with_encoding(method, url, **kwargs):
        """Wrapper for requests to handle encoding issues"""
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # Check if it's an encoding-related error
            if "quote_from_bytes" in str(e) or "encoding" in str(e).lower():
                print(f"Encoding error in request: {e}")
            raise

    """
    Generic GET/POST functions
    """
    def _get_projects(self, payload: dict) -> List[dict] | str:
        projects_payload = {'db': 'Categories'}
        projects_payload.update(payload)
        projects_selector = {'selector': projects_payload}
        print(f"Sending project request with payload:", projects_selector)
        projects_map = self.db.find(projects_selector)
        time.sleep(3)
        projects_dto = []

        # Collect all documents from the map into a list
        try:
            for doc in projects_map:
                projects_dto.append(doc)

            if not projects_dto:
                return "No projects returned!"

            return projects_dto
        except Exception as e:
            return f"Error retrieving projects: {str(e)}"

    def _get_tasks(self, payload: dict) -> str | list[Any]:
        day =  (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        tasks_payload = {'db': 'Tasks', 'day': {'$lte': day}}
        tasks_payload.update(payload)
        tasks_selector = {'selector': tasks_payload}
        print(f"Sending task request with payload:", tasks_selector)
        tasks_map = self.db.find(tasks_selector)
        time.sleep(3)
        tasks_list = list(tasks_map)
        if len(tasks_list) == 0:
            return "No tasks returned!"
        else:
            return tasks_list

    def _post_habit(self, habit_id: str, completion_time: Timecube, value: int) -> dict:
        url = f"{self.api_url}updateHabit"
        data = {
            "habitId": habit_id,
            "time": completion_time.date_in_ms,
            "value": value,
            "updateDB": True
        }
        print(f"Sending habit request with payload:", data)
        response = self._handle_request_with_encoding(
            requests.post,
            url,
            headers=self.api_headers,
            json=data
        )
        time.sleep(3)
        return response.json()

    def _post_value_to_tracker(self, tracker_id: str, time_of_habit: Timecube, value: int) -> List:
        print(f"Sending tracker request with payload:", tracker_id)
        tracker_document = self.db.get(tracker_id)
        time.sleep(3)
        tracker_history = tracker_document['history']

        tracker_history.append(time_of_habit.date_in_ms)
        tracker_history.append(value)
        tracker_document['history'] = tracker_history
        tracker_document['updatedAt'] = int(time() * 1000)

        print(f"Sending tracker update with payload:", tracker_document)
        response = self.db.update([tracker_document])
        time.sleep(3)
        return response

    def _delete_any_doc(self, doc_id: str) -> dict:
        url = f"{self.api_url}doc/delete"
        print(url)
        data = {
            "itemId": doc_id
        }
        print(f"Sending deletion request with payload:", data)
        response = requests.post(url, headers=self.api_headers, json=data)
        time.sleep(3)
        print(response.json())
        return response.json()

    """
    GET/POST/PATCH methods for databases with specific queries
    """
    def _get_project_by_id(self, am_id: str) -> dict:
        # Check cache first
        if am_id in self._project_cache:
            return self._project_cache[am_id]

        # If not in cache, make the API call
        project_payload = {'_id': am_id}
        projects = self._get_projects(project_payload)
        if isinstance(projects, str):
            raise Exception(projects)

        result = projects[0] if projects else {}

        # Store in cache
        self._project_cache[am_id] = result
        return result

    def _get_project_by_name(self, am_name: str) -> dict:
        project_payload = {'title': am_name}
        projects = self._get_projects(project_payload)
        if isinstance(projects, str):
            raise Exception(projects)
        return projects[0] if projects else {}

    def _get_task_by_id(self, task_id: str) -> dict:
        payload = {'_id': task_id}
        task = self._get_tasks(payload)[0]
        return task

    """
    Utility functions to modify or edit data, not specifically to GET or POST information to AM
    """
    def _set_pillar_value_goal_project(self, am_response: dict, dto: Task | Project) -> Task | Project:
        #if the parent is "unassigned" set Project to Inbox
        if am_response.get("parentId") == "unassigned":
            dto.project = "Inbox"

        #else parent = _get_project_by_id(parentId) and check type
        else:
            parent_response = self._get_project_by_id(am_response.get("parentId"))

            ##if parent.parentId = root set Pillar based on parent.title
            if parent_response.get("parentId") == "root":
                dto.pillar = parent_response.get("title")

            ##else check parent.type
            else:
                while parent_response.get("parentId") != "root":
                    ###if parent.type == category set Value Goal based on parent.title, then climb taxonomy
                    if parent_response.get("type") == "category":
                        dto.subcategory = parent_response.get("title")
                    ###if parent.type == project set Project based on parent.title, then climb taxonomy
                    if parent_response.get("type") == "project":
                        dto.project = parent_response.get("title")
                    parent_response = self._get_project_by_id(parent_response.get("parentId"))
                dto.pillar = parent_response.get("title")

        return dto

    def _replace_label_ids_with_label_titles(self, labels: List[str]) -> List[str]:
        # Populate label cache if it's empty
        if self._label_cache is None:
            url = f"{self.api_url}labels"
            print(f"Sending label request with url:", url)
            response = requests.get(url, headers=self.api_headers).json()
            time.sleep(3)

            self._label_cache = {}
            for item in response:
                key = item["_id"]
                value = item["title"]
                self._label_cache[key] = value

        # Use the cache to resolve labels
        resolved_labels = []
        for label in labels:
            if label in self._label_cache:
                resolved_label = self._label_cache[label]
            else:
                resolved_label = label
            resolved_labels.append(resolved_label)

        return resolved_labels

    def _replace_depends_on_id_with_title(self, am_response: dict) -> List[str]:
        dependencies = list(am_response["dependsOn"].keys())
        resolved_dependencies = []
        for item in dependencies:
            dependency_response = self._get_task_by_id(item)
            resolved_dependencies.append(dependency_response["title"])
        return resolved_dependencies

    def _replace_goal_id_with_goal_title(self, am_response: dict) -> List[str] | Exception:
        goal_ids = []
        goal_titles = []
        for key, value in am_response.items():
            match = re.match(r"g_in_(.+)", key)
            if match:
                goal_ids.append(match.group(1))

        if goal_ids:
            for goal_id in goal_ids:
                # Check cache first
                if goal_id in self._goal_cache:
                    goal_titles.append(self._goal_cache[goal_id])
                    continue

                # If not in cache, make the API call
                goal_payload = {'db': 'Goals', '_id': goal_id}
                goal_selector = {'selector': goal_payload}
                print(f"Sending goal request with payload:", goal_selector)
                goal_map = self.db.find(goal_selector)
                time.sleep(3)
                if goal_map is None:
                    return Exception("Goal id invalid!")

                for row in goal_map:
                    goal_title = row["title"]
                    goal_titles.append(goal_title)
                    # Store in cache
                    self._goal_cache[goal_id] = goal_title

        return goal_titles

    def _convert_task_response_to_dto(self, task_response: dict):
        task_dto = Task.from_am_json(task_response)

        if "dependsOn" in task_response:
            task_dto.depends_on = self._replace_depends_on_id_with_title(task_response)

        task_dto = self._set_pillar_value_goal_project(task_response, task_dto)
        task_dto.goal = self._replace_goal_id_with_goal_title(task_response)

        subtask_dtos = []
        if task_response.get("subtasks"):
            subtask: Subtask
            for item in task_response.get("subtasks"):
                subtask = Subtask.from_am_json(task_response.get("subtasks").get(item))
                subtask_dtos.append(subtask)
            task_dto.subtasks = subtask_dtos

        if "labelIds" in task_response:
            task_dto.tags = self._replace_label_ids_with_label_titles(task_response["labelIds"])

        if task_response.get("recurring"):
            if "Yearly" in task_dto.tags:
                task_dto.title = task_dto.title + " " + str(task_dto.day.date_in_datetime.year)
            if "Quarterly" in task_dto.tags:
                for label in task_dto.tags:
                    if label in ("Q1", "Q2", "Q3", "Q4"):
                        task_dto.planned_quarter = label + " 2025"
                        task_dto.title = task_dto.title + " " + label
            if "Monthly" in task_dto.tags:
                task_dto.title = task_dto.title + " - " + calendar.month_name[task_dto.day.date_in_datetime.month]
            if "Weekly" in task_dto.tags:
                task_dto.title = task_dto.title + " Week " + task_dto.day.week_number
            if "UnDaily" in task_dto.tags or "Daily" in task_dto.tags:
                task_dto.title = task_dto.title + " " + task_dto.day.date_Y_m_d

        return task_dto

    def _convert_project_response_to_dto(self, project_response: dict):
        project_dto = Project.from_am_json(project_response)

        project_dto = self._set_pillar_value_goal_project(project_response, project_dto)
        project_dto.goal = self._replace_goal_id_with_goal_title(project_response)

        if "labelIds" in project_response:
            project_response["labelIds"] = self._replace_label_ids_with_label_titles(project_response["labelIds"])
            for label in project_response["labelIds"]:
                if label in ("Q1", "Q2", "Q3", "Q4"):
                    project_dto.planned_quarter = label + " 2025"

        return project_dto

    """
    Public functions
    """
    def delete_task_by_id(self, task_id: str) -> dict:
        return self._delete_any_doc(task_id)

    def get_project_by_id(self, project_id: str) -> Project:
        project_response = self._get_project_by_id(project_id)
        project_dto =self._convert_project_response_to_dto(project_response)
        return project_dto

    def get_project_by_name(self, project_name: str) -> Project:
        project_response = self._get_project_by_name(project_name)
        project_dto =self._convert_project_response_to_dto(project_response)
        return project_dto

    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        day = (datetime.now().date() + timedelta(days=14)).strftime('%Y-%m-%d')
        payload = {'parentId': project_id, 'day': {'$lte': day}}
        tasks_list = self._get_tasks(payload)
        tasks = []
        for row in tasks_list:
            task_dto = self._convert_task_response_to_dto(row)
            tasks.append(task_dto)
        return tasks

    def get_tasks_by_scheduled(self, scheduled_date: Timecube) -> List[Task]:
        payload = {'day': scheduled_date.date_Y_m_d}
        tasks_map = self._get_tasks(payload)
        tasks = []
        for row in tasks_map:
            task_dto = self._convert_task_response_to_dto(row)
            tasks.append(task_dto)
        return tasks

    def get_tasks_by_last_updated(self, minutes_in_the_past: int):
        query_epoch = int((datetime.now() - timedelta(minutes=minutes_in_the_past)).timestamp() * 1000)
        payload = {'updatedAt': {'$gte': query_epoch}}
        tasks_map = self._get_tasks(payload)
        tasks = []
        for row in tasks_map:
            task_dto = self._convert_task_response_to_dto(row)
            tasks.append(task_dto)
        return tasks

    def get_next_seven_days_tasks(self, initial_date: Timecube) -> List[Task]:
        tasks = []
        current_date = initial_date.date_in_datetime
        week_hence_date = initial_date.date_in_datetime + timedelta(days=6)
        while current_date <= week_hence_date:
            this_days_tasks = self.get_tasks_by_scheduled(Timecube.from_datetime(current_date))
            tasks.extend(this_days_tasks)
            current_date = current_date + timedelta(days=1)
        return tasks

    def post_habit_by_title(self, title: str, completion_time: Timecube, value: int) -> dict | str:
        url = f"{self.api_url}habits?raw=1"
        print(f"Sending habit request with url:", url)
        habits_list = requests.get(url, headers=self.api_headers).json()
        time.sleep(3)
        habit_id = ""
        for habit in habits_list:
            if habit.get('title') == title:
                habit_id = habit.get('_id')
        if habit_id is None:
            return "Habit does not exist!"
        return self._post_habit(habit_id, completion_time, value)

    def post_daily_note(self, date: Timecube, note: str) -> tuple:
        note_payload = {'db': 'DayItems', '_id': 'di_' + date.date_Y_m_d, 'note': note}
        print(f"Sending note request with payload:", note_payload)
        response = self.db.save(note_payload)
        time.sleep(3)
        return response

    def post_value_to_tracker_by_title(self, tracker_title: str, time_of_habit: Timecube, value: int) -> List | str:
        tracker_selector = {'selector': {'db': 'Trackers'}}
        print(f"Sending tracker request with payload:", tracker_selector)
        tracker_list = self.db.find(tracker_selector)
        time.sleep(3)
        tracker_id = ""
        for tracker in tracker_list:
            if tracker['title'] == tracker_title:
                tracker_id = tracker['_id']
        if tracker_id is None:
            return "Invalid tracker title!"
        return self._post_value_to_tracker(tracker_id, time_of_habit, value)
