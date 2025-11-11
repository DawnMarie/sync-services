from dotenv import load_dotenv
from notion_client import Client

import os

class NotionConfig:
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
        self.value_goal_database_id = os.getenv("NOTION_SUBCATEGORY_DB_ID")
        self.goal_outcome_database_id = os.getenv("NOTION_GOAL_DB_ID")
        self.project_database_id = os.getenv("NOTION_PROJECT_DB_ID")
        self.tasks_database_id = os.getenv("NOTION_TASKS_DB_ID")
        self.week_database_id = os.getenv("NOTION_WEEK_DB_ID")
        self.month_database_id = os.getenv("NOTION_MONTH_DB_ID")
        self.quarter_database_id = os.getenv("NOTION_QUARTER_DB_ID")

        self.stepbet_database_id = os.getenv("NOTION_STEPBET_DB_ID")

        self.habit_database_id = os.getenv("NOTION_HABIT_DB_ID")
        self.mood_database_id = os.getenv("NOTION_MOOD_DB_ID")
        self.tracker_database_id = os.getenv("NOTION_TRACKERS_DB_ID")
        self.tracker_entry_database_id = os.getenv("NOTION_TRACKER_ENTRY_DB_ID")

        self.insight_block_id = os.getenv("NOTION_INSIGHT_BLOCK_ID")

