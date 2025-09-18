import logging
from datetime import datetime as dt, timedelta, timezone
from typing import Optional
from .clients import WildberriesClient
from .repository import ReviewRepository

logger = logging.getLogger(__name__)

class ReviewsCollector:
    def __init__(self, wb_client: WildberriesClient):
        self.wb = wb_client

    async def collect_bad_reviews(
        self,
        articul: int,
        min_rating: int = 3,
        days_back: int = 3,
    ) -> int:
        """
        Собирает «плохие» отзывы и складывает в БД.
        Возвращает количество ВСТАВЛЕННЫХ записей.
        """
        since = dt.now(tz=timezone.utc) - timedelta(days=days_back)
        total_inserted = 0

        async for raw in self.wb.fetch_reviews(articul):
            try:
                rating = int(raw.get("rating", 5))
                if rating >= min_rating:
                    continue
                created = dt.fromisoformat(raw["createdDate"].replace("Z", "+00:00"))
                if created < since:
                    continue

                inserted = ReviewRepository.merge_review(
                    articul=articul,
                    review_id=int(raw["id"]),
                    user_name=raw.get("wbUserDetails", {}).get("name", "Anonymous"),
                    rating=rating,
                    text=raw.get("text", "") or "",
                    created_date=created,
                )
                if inserted:
                    total_inserted += 1
            except Exception as exc:
                logger.warning("Skipping malformed review: %s", exc)
                continue

        logger.info("Articul %s: inserted %s new bad reviews", articul, total_inserted)
        return total_inserted