from data_models.insight import Insight
from services.notion.basic import NotionBasic


class NotionPageSpecific(NotionBasic):

    def _update_daily_insight(self, insight: Insight, insight_id: str, detail_id: str):
        return self._update_block_text(insight.insight, insight_id, "heading_2"), self._update_block_text(insight.detail, detail_id, "heading_3")

    def _update_weekly_insight(self, insight: Insight, insight_id: str, detail_id: str):
        return self._update_block_text(insight.insight, insight_id, "heading_3"), self._update_block_text(insight.detail, detail_id, "paragraph")

