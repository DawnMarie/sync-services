from data_models.timecube import Timecube
from services.exist import ExistService
from services.notion import NotionManager

from datetime import datetime, timedelta


def count_notion_tasks_and_send_to_exist():
        try:
            notion_service = NotionManager()
            exist_service = ExistService()
            today = Timecube.from_datetime(datetime.now())
            yesterday = Timecube.from_datetime(datetime.now() - timedelta(days=1))

            yesterday_tasks = notion_service.get_tasks_completed_by_date(yesterday)
            today_tasks, upcoming_week_tasks = notion_service.get_tasks_for_date_and_next_6_days(today)
            yesterday_count = len(yesterday_tasks)
            today_count = len(today_tasks)
            upcoming_week_count = len(upcoming_week_tasks)

            exist_service.post_tasks_completed(yesterday, yesterday_count)
            exist_service.post_tasks_planned(today, today_count)
            exist_service.post_next_7_days_task_count(today, upcoming_week_count)

        except Exception as e:
            print(f"Error updating task in Notion: {e}")


if __name__ == "__main__":
    count_notion_tasks_and_send_to_exist()
