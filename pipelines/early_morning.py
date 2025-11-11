# !/usr/bin/env python3
"""
Script to run early in the morning (around 6 AM) that synchronizes data between various services
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import Tuple

from data_models.task import Task
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


def tasks_are_different(am_task: Task, notion_task: Task) -> bool:
    """
    Compare two tasks to see if they are different.
    """
    # Compare the fields that we care about
    if am_task.title != notion_task.title:
        return True

    if am_task.done != notion_task.done:
        return True

    if am_task.time_estimate != notion_task.time_estimate:
        return True

    if am_task.duration != notion_task.duration:
        return True

    # Compare day if both tasks have it
    if am_task.day and notion_task.day:
        if am_task.day.date_Y_m_d != notion_task.day.date_Y_m_d:
            return True

    # Compare planned week
    if am_task.planned_week or notion_task.planned_week:
        if am_task.planned_week != notion_task.planned_week:
            return True

    # Compare planned month
    if am_task.planned_month or notion_task.planned_month:
        if am_task.planned_month != notion_task.planned_month:
            return True

    # Compare planned quarter
    if am_task.planned_quarter or notion_task.planned_quarter:
        if am_task.planned_quarter != notion_task.planned_quarter:
            return True

    # If one has a day and the other doesn't, they're different
    elif am_task.day or notion_task.day:
        return True

    # If we get here, the tasks are the same
    return False

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
    """Syncs Exist data to other services."""
    try:
        print("\nFetching data from Exist...")
        mood = exist_service.get_mood(yesterday)
        daily_note = exist_service.get_daily_note(yesterday)
        mobile_screen_time = exist_service.get_mobile_screen_time(yesterday)
        print(f"Retrieved mood: {mood}, screen time: {mobile_screen_time}")

        print("Updating Notion...")
        notion_service.update_daily_note(daily_note, yesterday)
        notion_service.update_mood_in_daily_tracking_and_mood_tracker(mood, yesterday)
        notion_service.update_mobile_screen_time(mobile_screen_time, yesterday)

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
        exist_service.post_number_of_events(yesterday, num_events)
        exist_service.post_time_in_events(yesterday, time_in_events)

        for event in events:
            if 'activism' in event.tags:
                exist_service.post_activism(yesterday)
            if 'coven' in event.tags:
                exist_service.post_coven(yesterday)
            if 'family' in event.tags:
                exist_service.post_family(yesterday)
            if 'guest' in event.tags:
                exist_service.post_guest(yesterday)
            if 'social' in event.tags:
                exist_service.post_social(yesterday)
        print("Successfully synced calendar data")
    except Exception as e:
        print(f"\nError syncing calendar data: {str(e)}")


def sync_garmin_to_exist(garmin_service: GarminService, exist_service: ExistService, yesterday: Timecube, today: Timecube) -> None:
    """Sync Garmin data to Exist."""
    try:
        print("\nFetching data from Garmin...")
        activities = garmin_service.get_workouts()
        yesterday_activities = [a for a in activities if
                                a.activity_date.date_in_datetime.date() == yesterday.date_in_datetime.date()]
        print(f"Retrieved {len(yesterday_activities)} activities")

        readiness_score, description = garmin_service.get_readiness(yesterday)
        stress = garmin_service.get_daily_average_stress(yesterday)
        hrv = garmin_service.get_hrv(today)
        print(f"Readiness: {readiness_score}, Stress: {stress}, HRV: {hrv}")

        print("Posting data to Exist...")
        exist_service.post_readiness(yesterday, readiness_score)
        exist_service.post_stress(yesterday, stress)
        exist_service.post_hrv(today, hrv)

        for activity in yesterday_activities:
            if activity.type == 'Running':
                exist_service.post_run(yesterday)
            if activity.type == 'Strength':
                exist_service.post_strength(yesterday)
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
        exist_service.post_declutter_time(yesterday, declutter_time)
        exist_service.post_yardwork_time(yesterday, yardwork_time)
        exist_service.post_cooking_time(yesterday, cooking_time)
        exist_service.post_witchcraft_time(yesterday, witchcraft_time)
        print("Successfully synced task data")
    except Exception as e:
        print(f"\nError syncing task data: {str(e)}")


def sync_garmin_to_notion(garmin_service: GarminService, notion_service: NotionManager, today: Timecube) -> None:
    """Sync Garmin data to Notion."""
    try:
        print("\nFetching Garmin data for Notion...")
        sleep_data = garmin_service.get_sleep(today)
        calories_out, _, steps, stress, total_distance = garmin_service.get_cals_out_sleep_steps_stress_total_distance(today)
        weight, body_fat = garmin_service.get_body_stats(today)
        hrv = garmin_service.get_hrv(today)
        cycle_day = garmin_service.get_menstrual_cycle(today)
        readiness_score, description = garmin_service.get_readiness(today)
        training_status = garmin_service.get_training_status(today)
        print(f"Retrieved - Weight: {weight}, Body Fat: {body_fat}, Cycle Day: {cycle_day}")

        print("Updating Notion...")
        notion_service.create_sleep_page(sleep_data)
        notion_service.create_steps_page(today, steps, total_distance)
        notion_service.create_today_training_page(training_status, readiness_score, description, stress)
        notion_service.update_weight_bodyfat_hrv_for_today(weight, body_fat, hrv)
        notion_service.update_menstrual_cycle_for_today(cycle_day)
        print("Successfully synced Garmin data to Notion")
    except Exception as e:
        print(f"\nError syncing Garmin data to Notion: {str(e)}")


def sync_am_to_notion_for_today(am_service: AmazingMarvinService, notion_service: NotionManager, today: Timecube) -> None:
    """
    Synchronize tasks from Amazing Marvin to Notion.
    """
    try:
        # Get tasks updated in Amazing Marvin in the last 12 hours
        am_tasks = am_service.get_tasks_by_scheduled(today)
        print(f"Found {len(am_tasks)} tasks scheduled in Amazing Marvin for today: {today.date_Y_m_d}")

        # For each task in Amazing Marvin
        for am_task in am_tasks:
            print(f"Processing task: {am_task}")
            # Find the corresponding task in Notion
            notion_task = notion_service.get_task_for_compare_and_sync(am_task.am_id)

            if notion_task != "No page returned!":
                # Task exists in Notion, check if it needs to be updated
                if tasks_are_different(am_task, notion_task):
                    # Tasks are different, update the Notion task with Amazing Marvin data
                    am_task.notion_id = notion_task.notion_id
                    notion_service.update_task_with_subtasks(am_task)
                    print(f"Updated task in Notion: {am_task.title}")
                else:
                    print(f"Task already up to date in Notion: {am_task.title}")
            else:
                # Task doesn't exist in Notion, create it
                task_id = notion_service.create_task_with_subtasks(am_task)
                if task_id:
                    am_task.notion_id = task_id
                    print(f"Created task in Notion: {am_task.title}")
        for am_task in am_tasks:
            if am_task.depends_on:
                notion_service.update_task_dependencies(am_task)

        print("Amazing Marvin to Notion synchronization completed successfully")
    except Exception as e:
        print(f"Error synchronizing Amazing Marvin to Notion: {e}")


def sync_current_tracker_data_to_am(am_service: AmazingMarvinService, notion_service: NotionManager, today: Timecube) -> None:
    try:
        print("\nFetching tracker data from Notion...")
        weight, bodyfat, heat_loan, credit_card, fed_student, prim_mort, sec_mort = notion_service.get_tracker_data()
        print(f"Retrieved data from Notion - Weight: {weight}, Body Fat: {bodyfat}, Heat Loan: {heat_loan}, ")

        # Update tracker data in Amazing Marvin
        am_service.post_value_to_tracker_by_title("Weight", today, weight)
        am_service.post_value_to_tracker_by_title("Body Fat Percentage", today, bodyfat)
        am_service.post_value_to_tracker_by_title("HEAT Loan", today, heat_loan)
        am_service.post_value_to_tracker_by_title("Credit Card", today, credit_card)
        am_service.post_value_to_tracker_by_title("Federal Student Loans", today, fed_student)
        am_service.post_value_to_tracker_by_title("Primary Mortgage", today, prim_mort)
        am_service.post_value_to_tracker_by_title("Secondary Mortgage", today, sec_mort)
        print("Successfully synced tracker data to Amazing Marvin")
    except Exception as e:
        print(f"\nError syncing Notion tracker data to Amazing Marvin: {str(e)}")


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

        #sync_exist_insights_to_notion(exist_service, notion_service)
        #sync_habits_to_am_and_exist(notion_service, am_service, exist_service, yesterday)
        #sync_exist_data_to_notion_and_am(exist_service, notion_service, am_service, yesterday)
        #sync_gcal_to_exist(gcal_service, exist_service, yesterday)
        #sync_garmin_to_exist(garmin_service, exist_service, yesterday, today)
        #sync_am_tasks_to_exist(am_service, exist_service, yesterday)
        #sync_garmin_to_notion(garmin_service, notion_service, today)
        sync_current_tracker_data_to_am(am_service, notion_service, today)
        sync_am_to_notion_for_today(am_service, notion_service, today)

        print("\n=== Morning sync completed successfully ===")
    except Exception as e:
        print(f"\n!!! Error in morning sync: {str(e)} !!!")
        raise e

if __name__ == "__main__":
    morning_sync()
