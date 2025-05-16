# !/usr/bin/env python3
"""
Script to run early in the morning (around 6 AM) that synchronizes data between various services
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import Tuple

from data_models.timecube import Timecube
from services.garmin import GarminService
from services.notion import NotionManager
from services.exist import ExistService
from services.amazing_marvin import AmazingMarvinService
from services.gcal import GoogleCalendarService


def get_today_and_yesterday() -> Tuple[Timecube, Timecube]:
    """Get Timecube objects for today and yesterday."""
    today = Timecube.from_datetime(datetime.now())
    yesterday = Timecube.from_datetime(datetime.now() - timedelta(days=1))
    return today, yesterday


def sync_exist_insights_to_notion(exist_service: ExistService, notion_service: NotionManager) -> None:
    """Pull insights from Exist and send them to Notion."""
    try:
        print("\nFetching insights from Exist...")
        insights = exist_service.get_insights()
        print(f"Retrieved {len(insights)} insights")
        notion_service.update_daily_insights_block(insights)
        print("Successfully posted insights to Notion")
    except Exception as e:
        print(f"\nError processing insights from Exist: {str(e)}")


def sync_habits_to_am_and_exist(notion_service: NotionManager, am_service: AmazingMarvinService,
                                exist_service: ExistService, yesterday: Timecube) -> None:
    """Sync habits between services."""
    try:
        print("\nFetching habits from Notion...")
        habits = notion_service.get_habits_from_daily_tracking_page_by_date(yesterday)
        print(f"Retrieved {len(habits)} habits")

        print("Posting habits to Exist...")
        exist_service.post_yesterdays_habits(habits)

        print("Posting habits to Amazing Marvin...")
        for key in habits:
            if key != "Drink Water":
                am_service.post_habit_by_title(key, yesterday, int(habits[key]))
        print("Successfully synced habits")
    except Exception as e:
        print(f"\nError syncing habits: {str(e)}")


def sync_exist_data_to_notion_and_am(exist_service: ExistService, notion_service: NotionManager,
                                     am_service: AmazingMarvinService, yesterday: Timecube) -> None:
    """Sync Exist data to other services."""
    try:
        print("\nFetching data from Exist...")
        mood = exist_service.get_yesterday_mood()
        daily_note = exist_service.get_yesterday_daily_note()
        mobile_screen_time = exist_service.get_yesterday_mobile_screen_time()
        print(f"Retrieved mood: {mood}, screen time: {mobile_screen_time}")

        print("Updating Notion...")
        notion_service.update_daily_note_for_yesterday(daily_note)
        notion_service.update_mood_in_daily_tracking_and_mood_tracker(mood)
        notion_service.update_mobile_screen_time_for_yesterday(mobile_screen_time)

        print("Updating Amazing Marvin...")
        am_service.post_daily_note(yesterday, daily_note)
        print("Successfully synced Exist data")
    except Exception as e:
        print(f"\nError syncing Exist data: {str(e)}")


def sync_gcal_to_exist(gcal_service: GoogleCalendarService, exist_service: ExistService, yesterday: Timecube) -> None:
    """Sync Google Calendar data to Exist."""
    try:
        print("\nFetching events from Google Calendar...")
        calendar_list = os.getenv("GOOGLE_CALENDARS").split(",")
        events = []
        for calendar in calendar_list:
            events_in_calendar = gcal_service.get_events_for_date(calendar, yesterday)
            if events_in_calendar:
                events.extend(events_in_calendar)

        print(f"Retrieved {len(events)} events")
        num_events = len(events)
        time_in_events = sum(event.duration for event in events if event.duration)

        print("Posting data to Exist...")
        exist_service.post_yesterday_number_of_events(num_events)
        exist_service.post_yesterday_time_in_events(time_in_events)

        for event in events:
            if 'activism' in event.tags:
                exist_service.post_yesterday_activism()
            if 'coven' in event.tags:
                exist_service.post_yesterday_coven()
            if 'family' in event.tags:
                exist_service.post_yesterday_family()
            if 'guest' in event.tags:
                exist_service.post_yesterday_guest()
            if 'social' in event.tags:
                exist_service.post_yesterday_social()
        print("Successfully synced calendar data")
    except Exception as e:
        print(f"\nError syncing calendar data: {str(e)}")


def sync_garmin_to_exist(garmin_service: GarminService, exist_service: ExistService, yesterday: Timecube) -> None:
    """Sync Garmin data to Exist."""
    try:
        print("\nFetching data from Garmin...")
        activities = garmin_service.get_workouts()
        yesterday_activities = [a for a in activities if
                                a.activity_date.date_in_datetime.date() == yesterday.date_in_datetime.date()]
        print(f"Retrieved {len(yesterday_activities)} activities")

        readiness_score, description = garmin_service.get_readiness(yesterday)
        stress = garmin_service.get_daily_average_stress(yesterday)
        print(f"Readiness: {readiness_score}, Stress: {stress}")

        print("Posting data to Exist...")
        exist_service.post_yesterday_readiness(readiness_score)
        exist_service.post_yesterday_stress(stress)

        for activity in yesterday_activities:
            if activity.type == 'Running':
                exist_service.post_yesterday_run()
            if activity.type == 'Strength':
                exist_service.post_yesterday_strength()
        print("Successfully synced Garmin data")
    except Exception as e:
        print(f"\nError syncing Garmin data: {str(e)}")


def sync_am_tasks_to_exist(am_service: AmazingMarvinService, exist_service: ExistService, yesterday: Timecube) -> None:
    """Sync Amazing Marvin tasks to Exist."""
    try:
        print("\nFetching tasks from Amazing Marvin...")
        tasks = am_service.get_tasks_by_scheduled(yesterday)
        print(f"Retrieved {len(tasks)} tasks")

        declutter_time = yardwork_time = cooking_time = witchcraft_time = 0

        for task in tasks:
            if task.done and task.day and task.day.date_in_datetime.date() == yesterday.date_in_datetime.date():
                if task.tags and 'Declutter' in task.tags:
                    declutter_time += task.duration if task.duration else 0
                if task.title == 'Yardwork':
                    yardwork_time += task.duration if task.duration else 0
                elif task.title == 'Cooking':
                    cooking_time += task.duration if task.duration else 0
                if task.subcategory == 'Witch':
                    witchcraft_time += task.duration if task.duration else 0

        print("Posting task times to Exist...")
        exist_service.post_today_declutter_time(declutter_time)
        exist_service.post_today_yardwork_time(yardwork_time)
        exist_service.post_today_cooking_time(cooking_time)
        exist_service.post_today_witchcraft_time(witchcraft_time)
        print("Successfully synced task data")
    except Exception as e:
        print(f"\nError syncing task data: {str(e)}")


def sync_garmin_to_notion(garmin_service: GarminService, notion_service: NotionManager, today: Timecube) -> None:
    """Sync Garmin data to Notion."""
    try:
        print("\nFetching Garmin data for Notion...")
        sleep_data = garmin_service.get_sleep(today)
        weight, body_fat = garmin_service.get_body_stats(today)
        cycle_day = garmin_service.get_menstrual_cycle(today)
        print(f"Retrieved - Weight: {weight}, Body Fat: {body_fat}, Cycle Day: {cycle_day}")

        print("Updating Notion...")
        notion_service.create_sleep_page(sleep_data)
        notion_service.update_weight_bodyfat_for_today(weight, body_fat)
        notion_service.update_menstrual_cycle_for_today(cycle_day)
        print("Successfully synced Garmin data to Notion")
    except Exception as e:
        print(f"\nError syncing Garmin data to Notion: {str(e)}")


def morning_sync() -> None:
    """Main function to run all morning sync tasks."""
    try:
        print("\n=== Starting Morning Sync ===")

        print("\nInitializing services...")
        garmin_service = GarminService()
        notion_service = NotionManager()
        exist_service = ExistService()
        am_service = AmazingMarvinService()
        gcal_service = GoogleCalendarService()

        today, yesterday = get_today_and_yesterday()
        print(f"Syncing data for {today.date_Y_m_d}")

        sync_exist_insights_to_notion(exist_service, notion_service)
        sync_habits_to_am_and_exist(notion_service, am_service, exist_service, yesterday)
        sync_exist_data_to_notion_and_am(exist_service, notion_service, am_service, yesterday)
        sync_gcal_to_exist(gcal_service, exist_service, yesterday)
        sync_garmin_to_exist(garmin_service, exist_service, yesterday)
        sync_am_tasks_to_exist(am_service, exist_service, yesterday)
        sync_garmin_to_notion(garmin_service, notion_service, today)

        print("\n=== Morning sync completed successfully ===")
    except Exception as e:
        print(f"\n!!! Error in morning sync: {str(e)} !!!")
        raise e


if __name__ == "__main__":
    morning_sync()