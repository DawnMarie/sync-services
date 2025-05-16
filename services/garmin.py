from data_models.activity import Activity
from data_models.personal_record import PR
from data_models.sleep import Sleep
from data_models.timecube import Timecube

from dotenv import load_dotenv
from garminconnect import Garmin
from typing import List
import os


class GarminService:
    load_dotenv()

    def __init__(self):
        garmin_email = os.getenv("GARMIN_EMAIL")
        garmin_password = os.getenv("GARMIN_PASSWORD")
        self.client = Garmin(garmin_email, garmin_password)
        self.client.login()

    def get_cals_out_sleep_stress_steps(self, day: Timecube):
        response = self.client.get_stats(day.date_Y_m_d)
        calories_out = response.get('activeKilocalories') + response.get('bmrKilocalories')
        sleep = (int(response.get('sleepingSeconds'))/60)/60
        steps = response.get('totalSteps')
        stress = response.get('averageStressLevel')
        total_distance = round(int(response.get('totalDistanceMeters')) * 0.000621371, 2)
        return calories_out, sleep, steps, stress, total_distance

    def get_sleep(self, day: Timecube):
        response = self.client.get_sleep_data(day.date_Y_m_d)
        sleep_dto = Sleep.from_garmin_json(response.get('dailySleepDTO'))
        sleep_dto.resting_hr = response.get('restingHeartRate')
        return sleep_dto

    def get_workouts(self) -> List[Activity]:
        response = self.client.get_activities(0, 25)
        activity_dtos = []
        for activity in response:
            activity_dto = Activity.from_garmin_json(activity)
            activity_dtos.append(activity_dto)
        return activity_dtos

    def get_body_stats(self, day: Timecube):
        response = self.client.get_daily_weigh_ins(day.date_Y_m_d)
        weight = int(response.get('dateWeightList')[0].get('weight')) * 0.00220462
        body_fat = int(response.get('dateWeightList')[0].get('bodyFat'))
        return weight, body_fat

    def get_training_status(self, day: Timecube):
        status_data = self.client.get_training_status(day.date_Y_m_d)
        most_recent = status_data.get("mostRecentTrainingStatus") \
            .get("latestTrainingStatusData") \
            .get("3485195778") \
            .get("trainingStatusFeedbackPhrase")
        daily_status = most_recent.split("_")[0].capitalize()
        return daily_status

    def get_readiness(self, day: Timecube):
        training_readiness: List[dict] = self.client.get_training_readiness(day.date_Y_m_d)
        score = training_readiness[0].get("score")
        description = training_readiness[0].get("feedbackShort").replace("_", " ").capitalize()
        return score, description

    def get_daily_average_stress(self, day: Timecube):
        response = self.client.get_all_day_stress(day.date_Y_m_d)
        stress = response.get('avgStressLevel')
        return stress

    def get_menstrual_cycle(self, day: Timecube):
        response = self.client.get_menstrual_data_for_date(day.date_Y_m_d)
        cycle_day = response.get('daySummary').get('dayInCycle')
        return cycle_day

    def get_prs(self) -> List[PR]:
        records = self.client.get_personal_record()
        filtered_records = []
        for record in records:
            if record.get('typeId') < 15:
                filtered_records.append(record)
        pr_dtos = []
        for item in filtered_records:
            record_dto = PR.from_garmin_json(item)
            pr_dtos.append(record_dto)
        return pr_dtos
