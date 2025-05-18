from data_models.insight import Insight
from data_models.timecube import Timecube

from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List
import os
import requests


class ExistService:
    load_dotenv()

    def __init__(self):
        self.url = 'https://exist.io/api/2/'
        self.headers = {'Authorization': 'Bearer ' + os.getenv("EXIST_TOKEN"), 'Content-Type': 'application/json'}

    def _get_attribute(self, attribute: str, day: Timecube):
        url = f"{self.url}attributes/values/"
        attribute_payload = {"attribute": [attribute], "date_max": day.date_Y_m_d}
        response = requests.get(url, headers=self.headers, params=attribute_payload)
        return response.json().get('results')

    def _post_attribute(self, attribute: str, attribute_date: Timecube, value: int):
        url = f"{self.url}attributes/update/"
        attribute_payload = {"name": attribute, "date": attribute_date.date_Y_m_d, "value": value}
        response = requests.post(url, headers=self.headers, json=attribute_payload)
        return response.json()

    def post_yesterday_tasks_completed(self, count: int):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("tasks_completed", yesterday, count)

    def post_yesterday_time_in_events(self, value: int):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("events_duration", yesterday, value)

    def post_yesterday_number_of_events(self, value: int):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("events", yesterday, value)

    def post_today_tasks_planned(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("tasks_planned", today, value)

    def post_today_tasks_completed(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("tasks_completed", today, value)

    def post_today_next_7_days_task_count(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("next_7_days", today, value)

    def post_today_declutter_time(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("declutter", today, value)

    def post_today_yardwork_time(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("yardwork", today, value)

    def post_today_cooking_time(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("cooking", today, value)

    def post_today_witchcraft_time(self, value: int):
        today = Timecube.from_datetime(datetime.today())
        return self._post_attribute("witchcraft", today, value)

    def post_yesterday_readiness(self, value: int):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("readiness", yesterday, value)

    def post_yesterday_stress(self, value: int):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("stress", yesterday, value)

    def post_yesterday_activism(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("activism", yesterday, 1)

    def post_yesterday_coven(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("coven", yesterday, 1)

    def post_yesterday_run(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("run", yesterday, 1)

    def post_yesterday_social(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("social", yesterday, 1)

    def post_yesterday_family(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("family", yesterday, 1)

    def post_yesterday_guest(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("guest", yesterday, 1)

    def post_yesterday_strength(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("strength", yesterday, 1)

    def post_yesterday_wfh(self):
        yesterday_datetime = (datetime.today() - timedelta(days=1))
        yesterday = Timecube.from_datetime(yesterday_datetime)
        return self._post_attribute("wfh", yesterday, 1)

    def get_insights(self) -> List[Insight]:
        url = f"{self.url}insights/"
        response = requests.get(url, headers=self.headers)
        insights = response.json().get('results')
        insights_dto = []
        for item in insights:
            insight_dto = Insight.from_exist_json(item)
            insights_dto.append(insight_dto)
        return insights_dto

    def get_yesterday_daily_note(self):
        yesterday = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        response = self._get_attribute("mood_note", yesterday)
        return response[0].get('value')

    def get_yesterday_mood(self):
        yesterday = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        response = self._get_attribute("mood", yesterday)
        return response[0].get('value')

    def get_yesterday_mobile_screen_time(self):
        yesterday = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        response =  self._get_attribute("mobile_screen_min", yesterday)
        return response[0].get('value')

    def post_yesterdays_habits(self, habits: dict):
        yesterday = Timecube.from_datetime(datetime.today() - timedelta(days=1))
        for key in habits:
            if key == "Vitamins & Supplements":
                self._post_attribute("vitamins", yesterday, habits.get(key))
            if key == "Prayers":
                self._post_attribute("prayer", yesterday, habits.get(key))
            if key == "Morning Hygiene":
                self._post_attribute("morning_hygiene", yesterday, habits.get(key))
            if key == "Evening Hygiene":
                self._post_attribute("evening_hygiene", yesterday, habits.get(key))
            if key == "Stick to Meal Plan":
                self._post_attribute("stick_to_meal_plan", yesterday, habits.get(key))
            if key == "Reading":
                pages_read = 10 if habits.get(key) == 1 else 0
                self._post_attribute("pages_read", yesterday, pages_read)
            if key == "Wear Night Guard":
                self._post_attribute("wear_night_guard", yesterday, habits.get(key))
            if key == "Progress Photo":
                self._post_attribute("progress_photo", yesterday, habits.get(key))
            if key == "Clean Kitchen":
                self._post_attribute("clean_kitchen", yesterday, habits.get(key))
