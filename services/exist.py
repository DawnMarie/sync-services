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

    ## Productivity Group
    def post_declutter_time(self, timecube: Timecube, value: int):
        return self._post_attribute("declutter", timecube, value)

    def post_next_7_days_task_count(self, timecube: Timecube, value: int):
        return self._post_attribute("next_7_days", timecube, value)

    def post_tasks_completed(self, timecube: Timecube, count: int):
        return self._post_attribute("tasks_completed", timecube, count)

    def post_tasks_planned(self, timecube: Timecube, value: int):
        return self._post_attribute("tasks_planned", timecube, value)

    def post_yardwork_time(self, timecube: Timecube, value: int):
        return self._post_attribute("yardwork", timecube, value)

    ## Events Group
    def post_number_of_events(self, timecube: Timecube, value: int):
        return self._post_attribute("events", timecube, value)

    def post_time_in_events(self, timecube: Timecube, value: int):
        return self._post_attribute("events_duration", timecube, value)

    ## Health and body Group
    def post_hrv(self, timecube: Timecube, value: int):
        return self._post_attribute("heartrate_variability", timecube, value)

    def post_witchcraft_time(self, timecube: Timecube, value: int):
        return self._post_attribute("witchcraft", timecube, value)

    ## Food and drink Group
    def post_cooking_time(self, timecube: Timecube, value: int):
        return self._post_attribute("cooking", timecube, value)

    def post_readiness(self, timecube: Timecube, value: int):
         return self._post_attribute("readiness", timecube, value)

    def post_stress(self, timecube: Timecube, value: int):
        return self._post_attribute("stress", timecube, value)

    ## Custom tabs Group
    def post_activism(self, timecube: Timecube):
        return self._post_attribute("activism", timecube, 1)

    def post_coven(self, timecube: Timecube):
        return self._post_attribute("coven", timecube, 1)

    def post_family(self, timecube: Timecube):
        return self._post_attribute("family", timecube, 1)

    def post_guest(self, timecube: Timecube):
         return self._post_attribute("guest", timecube, 1)

    def post_run(self, timecube: Timecube):
        return self._post_attribute("run", timecube, 1)

    def post_social(self, timecube: Timecube):
         return self._post_attribute("social", timecube, 1)

    def post_strength(self, timecube: Timecube):
        return self._post_attribute("strength", timecube, 1)

    def post_wfh(self, timecube: Timecube):
        return self._post_attribute("wfh", timecube, 1)

    def get_insights(self) -> List[Insight]:
        url = f"{self.url}insights/"
        response = requests.get(url, headers=self.headers)
        insights = response.json().get('results')
        insights_dto = []
        for item in insights:
            insight_dto = Insight.from_exist_json(item)
            insights_dto.append(insight_dto)
        return insights_dto

    def get_daily_note(self, timecube: Timecube) -> str:
        response = self._get_attribute("mood_note", timecube)
        return response[0].get('value')

    def get_mood(self, timecube: Timecube) -> int:
        response = self._get_attribute("mood", timecube)
        return response[0].get('value')

    def get_mobile_screen_time(self, timecube: Timecube) -> int:
        response =  self._get_attribute("mobile_screen_min", timecube)
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
