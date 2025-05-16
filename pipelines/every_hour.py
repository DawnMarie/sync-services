#!/usr/bin/env python3
"""
Script to run every hour that:
1. Pulls steps, calories out, activities, training status, training readiness, and daily average stress from Garmin
2. Updates the Daily Tracking page in Notion with this data
"""

from datetime import datetime
import logging

from data_models.timecube import Timecube
from services.garmin import GarminService
from services.notion import NotionManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('garmin_to_notion')


def get_today() -> Timecube:
    """
    Get a Timecube object for today.
    """
    return Timecube.from_datetime(datetime.now())


def sync_garmin_to_notion() -> None:
    """
    Pull data from Garmin and post it to Notion's Daily Tracking page.
    """
    try:
        # Initialize services
        garmin_service = GarminService()
        notion_service = NotionManager()

        # Get today
        today = get_today()

        logger.info(f"Syncing Garmin data to Notion for {today.date_Y_m_d}")

        try:
            # Get steps, calories out, and total distance
            calories_out, _, steps, _, total_distance = garmin_service.get_cals_out_sleep_steps_stress_total_distance(today)

            # Get training status
            training_status = garmin_service.get_training_status(today)

            # Get readiness
            readiness_score, readiness_description = garmin_service.get_readiness(today)

            # Get daily average stress
            stress = garmin_service.get_daily_average_stress(today)

            # Get activities
            activities = garmin_service.get_workouts()
            today_activities = [a for a in activities if a.activity_date.date_in_datetime.date() == today.date_in_datetime.date()]

            # Update Notion
            # Update steps and distance
            notion_service.update_steps_entries_for_today(steps, total_distance)

            # Update calories out
            notion_service.update_calories_out_in_daily_tracking(today, calories_out)

            # Update training status and readiness
            notion_service.update_training_entries_for_today(training_status, readiness_score, readiness_description, stress)

            # Update activities
            for activity in today_activities:
                notion_service.create_or_update_activity_page(activity)

            logger.info(f"Successfully posted Garmin data to Notion")
        except Exception as e:
            logger.error(f"Error processing Garmin data: {e}")

        logger.info("Garmin to Notion synchronization completed successfully")
    except Exception as e:
        logger.error(f"Error synchronizing Garmin to Notion: {e}")


if __name__ == "__main__":
    sync_garmin_to_notion()
