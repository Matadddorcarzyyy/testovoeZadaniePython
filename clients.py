import httpx
import logging
from datetime import datetime as dt, timedelta, timezone
from typing import AsyncGenerator, Dict, Any

logger = logging.getLogger(__name__)

class WildberriesClient:
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def fetch_reviews(self, articul: int) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Генератор по всем страницам отзывов WB.
        Возвращает «сырые» dict-и, дальше фильтруем уже в сервисе.
        """
        url = f"{self.base_url}/product/feedback"
        page = 1
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                try:
                    resp = await client.get(
                        url,
                        params={
                            "imtId": 0,  # можно оставить 0 – WB всё равно отдаёт по nmId
                            "nmId": articul,
                            "page": page,
                            "take": 100,
                            "order": "dateDesc",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    feedbacks = data.get("feedbacks", [])
                    if not feedbacks:
                        break
                    for item in feedbacks:
                        yield item
                    page += 1
                except httpx.HTTPStatusError as e:
                    logger.error("WB HTTP error %s on page %s", e.response.status_code, page)
                    break
                except Exception as exc:
                    logger.exception("Unexpected error while fetching page %s: %s", page, exc)
                    break