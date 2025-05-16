#!/usr/bin/env python3
"""
Script to run early in the morning (around 6 AM) that:
1. Pulls insights from Exist and sends them to Notion
2. Pulls habit data from yesterday's Daily Tracking page in Notion and sends to Amazing Marvin and Exist
3. Pulls mood, daily note, and mobile screen time from Exist for yesterday and sends to Notion and Amazing Marvin
4. Pulls the number of events, time in events, and event tags from Google Calendar and sends to Exist
5. Pulls activities, training status, training readiness, and daily average stress from Garmin and sends to Exist
6. Pulls time logged in tasks tagged "Declutter", titled "Yardwork" or "Cooking", or with the subcategory "Witch" from Amazing Marvin and sends to Exist
7. Pulls today's weight, body fat, sleep, and menstrual cycle data from Garmin and updates Notion
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import logging
from typing import Tuple

from data_models.timecube import Timecube
from data_models.insight import Insight
from services.garmin import GarminService
from services.notion import NotionManager
from services.exist import ExistService
from services.amazing_marvin import AmazingMarvinService
from services.gcal import GoogleCalendarService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='early_morning.log'
)
logger = logging.getLogger('early_morning')


def get_today_and_yesterday() -> Tuple[Timecube, Timecube]:
    """
    Get Timecube objects for today and yesterday.
    """
    today = Timecube.from_datetime(datetime.now())
    yesterday = Timecube.from_datetime(datetime.now() - timedelta(days=1))
    return today, yesterday


def sync_exist_insights_to_notion(exist_service: ExistService, notion_service: NotionManager) -> None:
    """
    Pull insights from Exist and send them to Notion.
    """
    try:
        insights = exist_service.get_insights()
        notion_service.update_daily_insights_block(insights)
        logger.info(f"Successfully posted {len(insights)} insights from Exist to Notion")
    except Exception as e:
        logger.error(f"Error processing insights from Exist: {e}")


def sync_habits_to_am_and_exist(notion_service: NotionManager, am_service: AmazingMarvinService, exist_service: ExistService, yesterday: Timecube) -> None:
    """
    Pull habit data from yesterday's Daily Tracking page in Notion and send to Amazing Marvin and Exist.
    Water data comes from a separate Notion table.
    """
    try:
        # Get habit data from Notion
        habits = notion_service.get_habits_from_daily_tracking_page_by_date(yesterday)

        # Send habits to Amazing Marvin and Exist
        exist_service.post_yesterdays_habits(habits)
        # Send it to Amazing Marvin
        for key in habits:
            if key != "Drink Water":
                am_service.post_habit_by_title(key, yesterday, int(habits[key]))

        logger.info(f"Successfully synced {len(habits)} habits from Notion to Amazing Marvin and Exist")
    except Exception as e:
        logger.error(f"Error syncing habits from Notion to Amazing Marvin and Exist: {e}")


def sync_exist_data_to_notion_and_am(exist_service: ExistService, notion_service: NotionManager, am_service: AmazingMarvinService, yesterday: Timecube) -> None:
    """
    Pull mood, daily note, and mobile screen time from Exist for yesterday and send to Notion and Amazing Marvin.
    """
    try:
        # Get yesterday's mood, daily note, and mobile screen time from Exist
        mood = exist_service.get_yesterday_mood()
        daily_note = exist_service.get_yesterday_daily_note()
        mobile_screen_time = exist_service.get_yesterday_mobile_screen_time()

        # Update Notion
        notion_service.update_daily_note_for_yesterday(daily_note)
        notion_service.update_mood_in_daily_tracking_and_mood_tracker(mood)
        notion_service.update_mobile_screen_time_for_yesterday(mobile_screen_time)

        # Update Amazing Marvin
        am_service.post_daily_note(yesterday, daily_note)

        logger.info(f"Successfully synced mood, daily note, and mobile screen time from Exist to Notion and Amazing Marvin")
    except Exception as e:
        logger.error(f"Error syncing data from Exist to Notion and Amazing Marvin: {e}")


def sync_gcal_to_exist(gcal_service: GoogleCalendarService, exist_service: ExistService, yesterday: Timecube) -> None:
    """
    Pull the number of events, time in events, and event tags from Google Calendar and send to Exist.
    """
    try:
        # Get events from Google Calendar for yesterday
        calendar_list = os.getenv("GOOGLE_CALENDARS").split(",")
        events = []
        for calendar in calendar_list:
            events_in_calendar = gcal_service.get_events_for_date(calendar, yesterday)
            if events_in_calendar:
                events.extend(events_in_calendar)

        # Calculate the number of events and time in events
        num_events = len(events)
        time_in_events = sum(event.duration for event in events if event.duration)

        # Send data to Exist
        exist_service.post_yesterday_number_of_events(num_events)
        exist_service.post_yesterday_time_in_events(time_in_events)

        # Process event tags:
        # For example, if an event has a specific tag, post a boolean attribute to Exist
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

        logger.info(f"Successfully synced {num_events} events from Google Calendar to Exist")
    except Exception as e:
        logger.error(f"Error syncing events from Google Calendar to Exist: {e}")


def sync_garmin_to_exist(garmin_service: GarminService, exist_service: ExistService, yesterday: Timecube) -> None:
    """
    Pull activities, training status, training readiness, and daily average stress from Garmin and send to Exist.
    """
    try:
        # Get data from Garmin
        activities = garmin_service.get_workouts()
        yesterday_activities = [a for a in activities if a.activity_date.date_in_datetime.date() == yesterday.date_in_datetime.date()]

        readiness_score, _ = garmin_service.get_readiness(yesterday)
        stress = garmin_service.get_daily_average_stress(yesterday)

        # Send data to Exist
        exist_service.post_yesterday_readiness(readiness_score)
        exist_service.post_yesterday_stress(stress)

        # Process activities
        for activity in yesterday_activities:
            if activity.type == 'Running':
                exist_service.post_yesterday_run()
            if activity.type == 'Strength':
                exist_service.post_yesterday_strength()

        logger.info(f"Successfully synced Garmin data to Exist")
    except Exception as e:
        logger.error(f"Error syncing Garmin data to Exist: {e}")


def sync_am_tasks_to_exist(am_service: AmazingMarvinService, exist_service: ExistService, yesterday: Timecube) -> None:
    """
    Pull time logged in tasks tagged "Declutter", titled "Yardwork" or "Cooking", or with subcategory "Witch" from Amazing Marvin and send to Exist.
    """
    try:
        # Get tasks from Amazing Marvin for yesterday
        tasks = am_service.get_tasks_by_scheduled(yesterday)

        # Filter and process tasks
        declutter_time = 0
        yardwork_time = 0
        cooking_time = 0
        witchcraft_time = 0

        for task in tasks:
            # Check if the task was completed yesterday
            if task.done and task.day and task.day.date_in_datetime.date() == yesterday.date_in_datetime.date():
                # Check for the "Declutter" tag
                if task.tags and 'Declutter' in task.tags:
                    declutter_time += task.duration if task.duration else 0

                # Check for "Yardwork" or "Cooking" title
                if task.title == 'Yardwork':
                    yardwork_time += task.duration if task.duration else 0
                elif task.title == 'Cooking':
                    cooking_time += task.duration if task.duration else 0

                # Check for "Witch" subcategory
                if task.subcategory == 'Witch':
                    witchcraft_time += task.duration if task.duration else 0

        # Send data to Exist
        exist_service.post_today_declutter_time(declutter_time)
        exist_service.post_today_yardwork_time(yardwork_time)
        exist_service.post_today_cooking_time(cooking_time)
        exist_service.post_today_witchcraft_time(witchcraft_time)

        logger.info(f"Successfully synced task data from Amazing Marvin to Exist")
    except Exception as e:
        logger.error(f"Error syncing task data from Amazing Marvin to Exist: {e}")


def sync_garmin_to_notion(garmin_service: GarminService, notion_service: NotionManager, today: Timecube) -> None:
    """
    Pull today's weight, body fat, sleep, and menstrual cycle data from Garmin and update Notion.
    """
    try:
        # Get data from Garmin
        sleep_data = garmin_service.get_sleep(today)
        weight, body_fat = garmin_service.get_body_stats(today)
        cycle_day = garmin_service.get_menstrual_cycle(today)

        # Update Notion ##invalid URL??
        notion_service.create_sleep_page(sleep_data)
        notion_service.update_weight_bodyfat_for_today(weight, body_fat)
        notion_service.update_menstrual_cycle_for_today(cycle_day)

        logger.info(f"Successfully synced Garmin data to Notion")
    except Exception as e:
        logger.error(f"Error syncing Garmin data to Notion: {e}")


def morning_sync() -> None:
    """
    Main function to run all the morning sync tasks.
    """
    try:
        # Initialize services
        garmin_service = GarminService()
        notion_service = NotionManager()
        exist_service = ExistService()
        am_service = AmazingMarvinService()
        gcal_service = GoogleCalendarService()

        # Get today and yesterday
        today, yesterday = get_today_and_yesterday()

        logger.info(f"Starting morning sync for {today.date_Y_m_d}")

        # 1. Pull insights from Exist and send them to Notion
        sync_exist_insights_to_notion(exist_service, notion_service)

        # 2. Pull habit data from yesterday's Daily Tracking page in Notion and send to Amazing Marvin and Exist
        sync_habits_to_am_and_exist(notion_service, am_service, exist_service, yesterday)

        # 3. Pull mood, daily note, and mobile screen time from Exist for yesterday and send to Notion and Amazing Marvin
        sync_exist_data_to_notion_and_am(exist_service, notion_service, am_service, yesterday)

        # 4. Pull the number of events, time in events, and event tags from Google Calendar and send to Exist
        sync_gcal_to_exist(gcal_service, exist_service, yesterday)

        # 5. Pull activities, training status, training readiness, and daily average stress from Garmin and send to Exist
        sync_garmin_to_exist(garmin_service, exist_service, yesterday)

        # 6. Pull time logged in tasks from Amazing Marvin and send to Exist
        sync_am_tasks_to_exist(am_service, exist_service, yesterday)

        # 7. Pull today's weight, body fat, sleep and menstrual cycle data from Garmin and update Notion
        sync_garmin_to_notion(garmin_service, notion_service, today)

        logger.info("Morning sync completed successfully")
    except Exception as e:
        logger.error(f"Error in morning sync: {e}")


if __name__ == "__main__":
    morning_sync()
