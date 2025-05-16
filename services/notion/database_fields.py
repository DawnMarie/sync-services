from services.notion.basic import NotionBasic
from data_models.timecube import Timecube

class NotionDatabaseFields(NotionBasic):
    """
    GET/POST/PATCH methods that return specific data fields on database pages
    """
    def _get_database_page_id_by_date(self, database_id: str, field_name: str, search_date: Timecube) -> str:
        page_id = "No page id returned!"
        page = self._get_database_pages_by_date_field(database_id, field_name, search_date)
        if page:
            page_id = page[0]['id']
        return page_id

    def _get_database_page_id_by_page_title(self, database_id: str, field_name: str, page_title: str) -> str:
        page_id = "No page id returned!"
        pages = self._get_database_pages_by_title(database_id, field_name, page_title)
        if pages.get("results").get(0).get("id"):
            page_id = pages.get("results").get(0).get("id")
        return page_id

    def _get_database_page_title_by_id(self, page_id: str, title_field: str):
        page_name = "No page returned!"
        page = self._get_page_by_id(page_id)
        if page:
            page_name = page.get("properties").get(title_field).get("title").get(0).get("plain_text")
        return page_name

