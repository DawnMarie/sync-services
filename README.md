# Sync Services

This repository contains scripts for synchronizing data between various services.

## Task Synchronization between Amazing Marvin and Notion

The `pipelines/every_fifteen_minutes.py` script synchronizes tasks between Amazing Marvin and Notion. It pulls tasks that have been updated since the last run from both services and ensures that each service has the most recent changes.

### Features

- Bi-directional synchronization between Amazing Marvin and Notion
- Tracks the last run timestamp to only process recently updated tasks
- Handles task creation, updates, and conflict resolution
- Logs all operations for debugging and monitoring

### Setup

1. Ensure you have the required dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   NOTION_API_KEY=your_notion_api_key
   AMAZING_MARVIN_API_KEY=your_amazing_marvin_api_key
   ```

### Usage

To run the script manually:

```
python pipelines/every_fifteen_minutes.py
```

To set up a cron job to run the script every 15 minutes:

```
*/15 * * * * cd /path/to/sync-services && python pipelines/every_fifteen_minutes.py
```

### How It Works

1. The script retrieves the timestamp of the last run from a file (`last_run_timestamp.json`).
2. It fetches tasks that have been updated since the last run from both Amazing Marvin and Notion.
3. For each task updated in Amazing Marvin:
   - If the task exists in Notion and the Amazing Marvin version is more recent, it updates the Notion task.
   - If the task doesn't exist in Notion, it creates a new task in Notion.
4. For each task updated in Notion:
   - If the task exists in Amazing Marvin and the Notion version is more recent, it updates the Amazing Marvin task.
   - If the task doesn't exist in Amazing Marvin, it creates a new task in Amazing Marvin.
5. The script saves the current timestamp as the last run timestamp.

### Logging

The script logs all operations to a file named `sync_tasks.log`. You can check this file for information about the synchronization process, including any errors that occurred.

### Notes

Version 0.9 - everything works, mostly. Lots of cleanup and additions needed.