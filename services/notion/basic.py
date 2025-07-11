from data_models.timecube import Timecube
from services.notion.config import NotionConfig

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any

class NotionBasic(NotionConfig):
    """
    Generic GET/POST functions for Notion
    """

    def __init__(self):
        super().__init__()
        # Add cache dictionaries
        self._page_cache = {}  # Cache for pages by ID
        self._database_query_cache = {}  # Cache for database queries

    def _generate_cache_key(self, *args) -> str:
        """Generate a cache key from the arguments"""
        return str(hash(str(args)))

    def _get_database_pages_by_checkbox_field(self, database_id: str, field_name: str, field_value: bool) -> str | List[
        dict]:
        # Generate cache key
        cache_key = self._generate_cache_key("checkbox", database_id, field_name, field_value)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        pages = "No page returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "checkbox": {"equals": field_value}
                }]
            }
        )
        if query['results']:
            pages = query['results']

        # Store in cache
        self._database_query_cache[cache_key] = pages
        return pages

    def _get_database_pages_by_date_field(self, database_id: str, field_name: str, field_value: Timecube) -> str | List[dict]:
        # Generate cache key
        cache_key = self._generate_cache_key("date", database_id, field_name, field_value.date_Y_m_d)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        pages = "No page returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "date": {"equals": field_value.date_Y_m_d}
                }]
            }
        )
        if query['results']:
            pages = query['results']

        # Store in cache
        self._database_query_cache[cache_key] = pages
        return pages

    def _get_database_pages_by_last_edited(self, database_id: str, minutes_in_the_past: int) -> List[dict]:
        # Note: Caching for this method has limited effectiveness since it depends on the current time
        # Generate cache key - include a timestamp rounded to the nearest minute to allow some caching
        current_minute = int(datetime.now().timestamp() / 60)
        cache_key = self._generate_cache_key("last_edited", database_id, minutes_in_the_past, current_minute)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        search_datetime = datetime.now() - timedelta(minutes=minutes_in_the_past)
        pages = []
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "timestamp": "last_edited_time",
                    "last_edited_time": {
                    "on_or_after": search_datetime.isoformat(timespec='seconds')
                },
            }
        )
        if query['results']:
            pages = query['results']

        # Store in cache
        self._database_query_cache[cache_key] = pages
        return pages

    def _get_database_pages_by_start_and_end_date_field(self, database_id: str, start_date: Timecube, end_date: Timecube) -> str | List[dict]:
        # Generate cache key
        cache_key = self._generate_cache_key("start_end_date", database_id, start_date.date_Y_m_d, end_date.date_Y_m_d)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        pages = "No page returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [
                    {"property": "Start Date", "date": {"on_or_before": start_date.date_Y_m_d}},
                    {"property": "End Date", "date": {"on_or_after": end_date.date_Y_m_d}}
                ]
            }
        )
        if query['results']:
            pages = query['results']

        # Store in cache
        self._database_query_cache[cache_key] = pages
        return pages

    def _get_database_pages_by_text_field(self, database_id: str, field_name: str, field_value: str) -> str | List[dict]:
        # Generate cache key
        cache_key = self._generate_cache_key("text", database_id, field_name, field_value)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        pages = "No page returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "rich_text": {"contains": field_value}
                }]
            }
        )
        if query['results']:
            pages = query['results']

        # Store in cache
        self._database_query_cache[cache_key] = pages
        return pages

    def _get_database_pages_by_title(self, database_id: str, field_name: str, page_title: str) -> str | List[dict]:
        # Generate cache key
        cache_key = self._generate_cache_key("title", database_id, field_name, page_title)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        pages = "No page returned!"
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [{
                    "property": field_name,
                    "title": {"contains": page_title}
                }]
            }
        )
        if query['results']:
            pages = query['results']

        # Store in cache
        self._database_query_cache[cache_key] = pages
        return pages

    def _get_block_children_by_id(self, block_id: str) -> List[dict]:
        # Generate cache key
        cache_key = self._generate_cache_key("block_children", block_id)

        # Check cache first
        if cache_key in self._database_query_cache:
            return self._database_query_cache[cache_key]

        # If not in cache, make the API call
        blocks = []
        query = self.client.blocks.children.list(
            block_id=block_id
        )
        for item in query["results"]:
            block = {"id": item["id"], "type": item["type"]}
            blocks.append(block)

        # Store in cache
        return blocks

    def _get_page_by_id(self, page_id: str) -> str | dict:
        # Check cache first
        if page_id in self._page_cache:
            return self._page_cache[page_id]

        # If not in cache, make the API call
        page = "No page returned!"
        query = self.client.pages.retrieve(page_id=page_id)
        if query:
            page = query
            # Store in cache
            self._page_cache[page_id] = page
        return page

    def _delete_page_by_id(self, page_id: str):
        return self.client.pages.update(page_id=page_id, archived=True)

    def _update_block_text(self, text: str, block_id: str, block_type: str):
        properties = {
            "rich_text": [{
                "text": {"content": text},
                "plain_text": text
            }]
        }
        update = {
            "block_id": block_id,
            block_type: properties
        }
        return self.client.blocks.update(**update)

    def _update_database_page(self, page_id: str, fields: dict):
        update = {
            "page_id": page_id,
            "properties": fields
        }
        return self.client.pages.update(**update)

    def _update_page_icon(self, page_id: str, icon: dict):
        update = {
            "page_id": page_id,
            "icon": icon
            }
        return self.client.pages.update(**update)

    def _post_new_database_page(self, database_id: str, properties: dict) -> dict:
        page = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        return self.client.pages.create(**page)
