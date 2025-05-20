#!/usr/bin/env python3
"""
Script to pull tasks updated in Amazing Marvin over the last 12 hours and update Notion.
This script is designed to be run periodically by a cron job.
"""

import logging

from data_models.timecube import Timecube
from services.amazing_marvin import AmazingMarvinService
from services.notion import NotionManager
from data_models.task import Task

from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('am_to_notion')


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


def delete_tasks_from_notion_and_am() -> None:
    """
    Check for tasks with the Delete checkbox checked in Notion and delete them from both Notion and Amazing Marvin.
    """
    try:
        # Initialize services
        am_service = AmazingMarvinService()
        notion_service = NotionManager()

        # Get tasks with the Delete checkbox checked
        tasks_to_delete = notion_service.get_tasks_to_delete()
        print(f"Found {len(tasks_to_delete)} tasks to delete")

        # For each task to delete
        for task in tasks_to_delete:
            # Mark the task as in_trash in Notion
            response = notion_service.delete_task(task)
            print(f"Marked task as in_trash in Notion: {task.title}")

            # Delete the task in Amazing Marvin if it exists
            if task.am_id:
                response = am_service.delete_task_by_id(task.am_id)
                print(f"Deleted task in Amazing Marvin: {task.title}")

        print("Task deletion completed successfully")
    except Exception as e:
        print(f"Error deleting tasks: {e}")


def sync_am_to_notion() -> None:
    """
    Synchronize tasks from Amazing Marvin to Notion.
    """
    try:
        # Initialize services
        am_service = AmazingMarvinService()
        notion_service = NotionManager()

        # Get tasks updated in Amazing Marvin in the last 30 minutes
        am_tasks = am_service.get_tasks_by_last_updated(30)
        print(f"Found {len(am_tasks)} tasks updated in Amazing Marvin in the last 45 minutes")

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


if __name__ == "__main__":
    delete_tasks_from_notion_and_am()
    sync_am_to_notion()
