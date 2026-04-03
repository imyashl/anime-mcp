"""
MangaDex API client — https://api.mangadex.org
Free, no authentication required for public endpoints.
"""

import time
from typing import Any, Optional
import httpx

BASE_URL = "https://api.mangadex.org"
READER_BASE = "https://mangadex.org/chapter"

_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 300


def _cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _cache_set(key: str, data: Any):
    _cache[key] = (time.time(), data)


async def _get(path: str, params: dict | None = None) -> dict:
    cache_key = f"{path}:{params}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{BASE_URL}{path}", params=params)
        resp.raise_for_status()
        data = resp.json()
    _cache_set(cache_key, data)
    return data


async def search_manga(title: str, limit: int = 5) -> list[dict]:
    """Search manga by title, returns list of manga with IDs."""
    data = await _get("/manga", {
        "title": title,
        "limit": limit,
        "order[relevance]": "desc",
        "includes[]": ["author", "cover_art"],
        "availableTranslatedLanguage[]": "en",
    })
    results = []
    for manga in data.get("data", []):
        attrs = manga.get("attributes", {})
        title_obj = attrs.get("title", {})
        en_title = title_obj.get("en") or next(iter(title_obj.values()), "Unknown")
        results.append({
            "id": manga["id"],
            "title": en_title,
            "status": attrs.get("status", "unknown"),
            "year": attrs.get("year"),
            "tags": [
                t["attributes"]["name"].get("en", "")
                for t in attrs.get("tags", [])
                if t.get("attributes", {}).get("name", {}).get("en")
            ][:6],
        })
    return results


async def get_manga_chapters(manga_id: str, limit: int = 20,
                              offset: int = 0) -> list[dict]:
    """Fetch chapter list for a manga ID."""
    data = await _get("/chapter", {
        "manga": manga_id,
        "limit": limit,
        "offset": offset,
        "translatedLanguage[]": "en",
        "order[chapter]": "asc",
    })
    chapters = []
    for ch in data.get("data", []):
        attrs = ch.get("attributes", {})
        chapters.append({
            "id": ch["id"],
            "chapter": attrs.get("chapter", "?"),
            "title": attrs.get("title") or f"Chapter {attrs.get('chapter', '?')}",
            "pages": attrs.get("pages", 0),
            "publishAt": attrs.get("publishAt", ""),
            "reading_url": f"{READER_BASE}/{ch['id']}",
        })
    return chapters


async def get_chapter_reading_link(manga_title: str, chapter_num: float) -> dict:
    """Find the MangaDex reading URL for a specific chapter number."""
    mangas = await search_manga(manga_title, limit=3)
    if not mangas:
        return {"error": f"Manga '{manga_title}' not found on MangaDex."}
    manga_id = mangas[0]["id"]
    manga_name = mangas[0]["title"]

    data = await _get("/chapter", {
        "manga": manga_id,
        "chapter": str(chapter_num),
        "translatedLanguage[]": "en",
        "limit": 5,
    })
    chapters = data.get("data", [])
    if not chapters:
        return {"error": f"Chapter {chapter_num} of '{manga_name}' not found in English."}

    ch = chapters[0]
    ch_id = ch["id"]
    return {
        "manga": manga_name,
        "chapter": chapter_num,
        "reading_url": f"{READER_BASE}/{ch_id}",
        "pages": ch.get("attributes", {}).get("pages", "?"),
    }
