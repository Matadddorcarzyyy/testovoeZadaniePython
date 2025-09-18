import asyncio
import logging
from datetime import timedelta
from wb_reviews.settings import settings
from wb_reviews.clients import WildberriesClient
from wb_reviews.services import ReviewsCollector
from wb_reviews.db import engine
from wb_reviews.models import Base

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

async def main(articul: int, min_rating: int = 3, days: int = 3):
    # создаём таблицы, если ещё не созданы
    Base.metadata.create_all(bind=engine)

    wb_client = WildberriesClient(base_url=settings.wb_base_url)
    collector = ReviewsCollector(wb_client)

    await collector.collect_bad_reviews(
        articul=articul,
        min_rating=min_rating,
        days_back=days,
    )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WB bad-reviews collector")
    parser.add_argument("articul", type=int, help="WB артикул (nmId)")
    parser.add_argument("--min-rating", type=int, default=3, help="максимальный «плохой» рейтинг")
    parser.add_argument("--days", type=int, default=3, help="глубина дней")
    args = parser.parse_args()

    asyncio.run(main(args.articul, args.min_rating, args.days))