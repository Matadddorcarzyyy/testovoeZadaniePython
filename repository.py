import logging
from datetime import datetime as dt
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select
from .db import SessionLocal
from .models import Review

logger = logging.getLogger(__name__)

class ReviewRepository:
    @staticmethod
    def merge_review(
        articul: int,
        review_id: int,
        user_name: str,
        rating: int,
        text: str,
        created_date: dt,
    ) -> bool:
        """
        UPSERT отзыва. Возвращает True, если запись была вставлена (не обновлена).
        """
        with SessionLocal.begin() as session:
            stmt = pg_insert(Review).values(
                id=review_id,
                articul=articul,
                user_name=user_name,
                rating=rating,
                text=text,
                created_date=created_date,
            ).on_conflict_do_nothing(index_elements=["id"])
            result = session.execute(stmt)
            inserted = result.rowcount == 1
            if inserted:
                logger.debug("Inserted new review %s", review_id)
            return inserted