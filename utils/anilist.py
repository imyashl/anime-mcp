"""
AniList GraphQL API client — https://graphql.anilist.co
Free, no authentication required.
"""

import time
from typing import Any, Optional
import httpx

ANILIST_URL = "https://graphql.anilist.co"

_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 180  # 3 minutes


def _cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _cache_set(key: str, data: Any):
    _cache[key] = (time.time(), data)


async def anilist_query(query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query against AniList."""
    cache_key = f"{query[:60]}:{variables}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    payload = {"query": query, "variables": variables or {}}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(ANILIST_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
    _cache_set(cache_key, data)
    return data


# ── Query definitions ─────────────────────────────────────────────────────────

TRENDING_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(sort: TRENDING_DESC, type: ANIME) {
      id
      title { romaji english native }
      trending
      popularity
      averageScore
      episodes
      status
      genres
      season
      seasonYear
      coverImage { large }
      siteUrl
    }
  }
}
"""

SEASONAL_QUERY = """
query ($season: MediaSeason, $year: Int, $page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(season: $season, seasonYear: $year, type: ANIME, sort: POPULARITY_DESC) {
      id
      title { romaji english }
      averageScore
      popularity
      episodes
      status
      genres
      studios { nodes { name } }
      coverImage { large }
      siteUrl
    }
  }
}
"""

RECOMMENDATIONS_BY_GENRE_QUERY = """
query ($genres: [String], $minScore: Int, $page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(genre_in: $genres, averageScore_greater: $minScore,
          type: ANIME, sort: POPULARITY_DESC) {
      id
      title { romaji english }
      averageScore
      popularity
      episodes
      status
      genres
      description(asHtml: false)
      coverImage { large }
      siteUrl
    }
  }
}
"""


async def get_trending_anime(limit: int = 10) -> list[dict]:
    data = await anilist_query(TRENDING_QUERY, {"page": 1, "perPage": limit})
    return data.get("data", {}).get("Page", {}).get("media", [])


async def get_seasonal_anilist(season: str, year: int, limit: int = 20) -> list[dict]:
    """season must be WINTER | SPRING | SUMMER | FALL (AniList format)."""
    data = await anilist_query(
        SEASONAL_QUERY,
        {"season": season.upper(), "year": year, "page": 1, "perPage": limit},
    )
    return data.get("data", {}).get("Page", {}).get("media", [])


async def get_recommendations_by_genre(genres: list[str], min_score: float = 7.0,
                                        limit: int = 10) -> list[dict]:
    min_score_int = int(min_score * 10)  # AniList uses 0-100 scale
    data = await anilist_query(
        RECOMMENDATIONS_BY_GENRE_QUERY,
        {"genres": genres, "minScore": min_score_int, "page": 1, "perPage": limit},
    )
    return data.get("data", {}).get("Page", {}).get("media", [])
