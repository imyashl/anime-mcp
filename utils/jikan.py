"""
Jikan API v4 client — https://api.jikan.moe/v4
Rate limit: 3 requests/second, 60/minute
"""

import asyncio
import time
from typing import Any, Optional
import httpx

BASE_URL = "https://api.jikan.moe/v4"

# Simple in-memory cache: {cache_key: (timestamp, data)}
_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 300  # seconds (5 min)

# Rate limiter state
_last_requests: list[float] = []
RATE_LIMIT = 3  # requests/second


async def _rate_limit():
    """Ensures we don't exceed 3 req/sec for Jikan."""
    now = time.monotonic()
    # Remove timestamps older than 1 second
    _last_requests[:] = [t for t in _last_requests if now - t < 1.0]
    if len(_last_requests) >= RATE_LIMIT:
        sleep_for = 1.0 - (now - _last_requests[0])
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)
    _last_requests.append(time.monotonic())


def _cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _cache_set(key: str, data: Any):
    _cache[key] = (time.time(), data)


async def jikan_get(path: str, params: dict | None = None) -> dict:
    """
    Core GET helper for Jikan API. Returns parsed JSON dict.
    Raises httpx.HTTPStatusError on non-2xx.
    """
    cache_key = f"{path}?{params}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    await _rate_limit()
    url = f"{BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        for attempt in range(3):
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                data = resp.json()
                _cache_set(cache_key, data)
                return data
            except httpx.TimeoutException:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)
    raise RuntimeError(f"Failed to fetch {url} after 3 attempts")


# ── Convenience wrappers ──────────────────────────────────────────────────────

async def search_anime(query: str, genre: str | None = None,
                       year: int | None = None,
                       status: str | None = None,
                       page: int = 1) -> dict:
    params: dict[str, Any] = {"q": query, "page": page, "limit": 10}
    if year:
        params["start_date"] = f"{year}-01-01"
        params["end_date"] = f"{year}-12-31"
    if status:
        params["status"] = status
    # Jikan genre filtering by name requires a genre list first
    # We handle genre filtering in the tool layer after fetching
    return await jikan_get("/anime", params)


async def search_manga(query: str, page: int = 1) -> dict:
    params: dict[str, Any] = {"q": query, "page": page, "limit": 10}
    return await jikan_get("/manga", params)


async def search_characters(query: str) -> dict:
    return await jikan_get("/characters", {"q": query, "limit": 10})


async def search_producers(query: str) -> dict:
    return await jikan_get("/producers", {"q": query, "limit": 10})


async def get_anime_by_id(anime_id: int) -> dict:
    return await jikan_get(f"/anime/{anime_id}/full")


async def get_manga_by_id(manga_id: int) -> dict:
    return await jikan_get(f"/manga/{manga_id}/full")


async def get_character_by_id(character_id: int) -> dict:
    return await jikan_get(f"/characters/{character_id}/full")


async def get_anime_episodes(anime_id: int, page: int = 1) -> dict:
    return await jikan_get(f"/anime/{anime_id}/episodes", {"page": page})


async def get_anime_staff(anime_id: int) -> dict:
    return await jikan_get(f"/anime/{anime_id}/staff")


async def get_anime_reviews(anime_id: int, page: int = 1) -> dict:
    return await jikan_get(f"/anime/{anime_id}/reviews", {"page": page})


async def get_anime_recommendations(anime_id: int) -> dict:
    return await jikan_get(f"/anime/{anime_id}/recommendations")


async def get_top_anime(filter_type: str = "bypopularity", page: int = 1) -> dict:
    """filter_type: airing | upcoming | bypopularity | favorite"""
    return await jikan_get("/top/anime", {"filter": filter_type, "page": page, "limit": 25})


async def get_top_manga(filter_type: str = "bypopularity", page: int = 1) -> dict:
    return await jikan_get("/top/manga", {"filter": filter_type, "page": page, "limit": 25})


async def get_seasonal_anime(year: int, season: str) -> dict:
    """season: winter | spring | summer | fall"""
    return await jikan_get(f"/seasons/{year}/{season}")


async def get_current_season() -> dict:
    return await jikan_get("/seasons/now")


async def get_upcoming_season() -> dict:
    return await jikan_get("/seasons/upcoming")


async def get_random_anime() -> dict:
    return await jikan_get("/random/anime")


async def get_genres() -> dict:
    return await jikan_get("/genres/anime")
